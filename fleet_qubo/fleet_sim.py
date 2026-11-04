"""Multi-robot closed-loop simulator built on the Ask or Act offline simulator.

Each robot drives its own Ask or Act scenario (its own pedestrian), stepped in
lockstep on a shared global clock. The step logic is copied line for line from
simulate_policies.simulate(); a test checks that one robot reproduces it exactly.

Couplings that are simulated:
  * One operator answers all questions, one at a time (FCFS), `service` s each.
    A question asked while the operator is busy waits; if no answer arrives within
    the Ask or Act answer timeout (5 s) the robot falls back to the cautious rule.
  * Joint mode: every robot holds at its decision deadline until the epoch closes
    (all robots have arrived, or `window` s have passed). The joint solver then
    assigns go / stop / ask to every robot in the epoch.

Couplings that are measured, not simulated: congestion time on a single corridor
(both neighbours halted at once). Robots run on separate lanes, so a halted robot
does not physically block its neighbour.

Policies:
  independent  the unchanged Ask or Act threshold policy (early confident commits,
               ask at the deadline), sharing the operator
  joint        no early commits; observes to the deadline, then follows the joint
               assignment. After a "go", the Ask or Act reflex still stops the robot
               if the smoothed probability rises to p_high.
"""
from __future__ import annotations

import math
import random

from .instances import GO, STOP, ASK

DT = 0.05
OBS_EVERY = 2            # tracker at 10 Hz
START_DELAY = 2.0
MAX_DURATION = 60.0


def make_policy_class(AskOrActPolicy):
    """Subclass the Ask or Act policy (imported from its repository at run time)."""

    import sys as _sys
    _compute_features = _sys.modules[AskOrActPolicy.__module__].compute_features

    class FleetPolicy(AskOrActPolicy):
        def __init__(self, model, calibrator, mode="independent", **kw):
            super().__init__("threshold", model, calibrator, **kw)
            self.mode = mode
            self.assigned = {}          # hid -> GO / STOP / ASK
            self.request = None         # (hid, p) when waiting for the epoch
            self.held_steps = 0
            self.n_obs = {}             # observations ever added, per pedestrian

        def add_observation(self, hid, t, x, y):
            super().add_observation(hid, t, x, y)
            self.n_obs[hid] = self.n_obs.get(hid, 0) + 1

        def predict(self, hid):
            """Ask or Act's predict(), with its cache fixed.

            The original caches on len(self.obs[hid]). That length stops changing once the
            40-observation history is full, so every later call returned the first prediction made
            after the buffer filled: the probability froze at engagement and smoothing never acted.
            The cache is keyed here on the number of observations ever added; everything else is
            unchanged."""
            import numpy as np
            n = self.n_obs.get(hid, 0)
            if self.p_cache.get(hid, (None,))[0] == n:
                return self.p_cache[hid][1]
            f = _compute_features(self.obs[hid])
            if f is None:
                return None
            p = _fast_probability(self.model, self.calibrator, f)
            hist = self.p_hist.setdefault(hid, [])
            hist.append(p)
            del hist[:-self.smooth_n]
            p = float(np.mean(hist))
            self.p_cache[hid] = (n, p)
            return p

        def decide(self, t, robot_x):
            if self.mode == "independent":
                return super().decide(t, robot_x)
            return self._decide_joint(t, robot_x)

        def _decide_joint(self, t, robot_x):
            import numpy as np
            go, reason, to_ask = True, "no engaged pedestrian", []
            for hid, ob in self.obs.items():
                if len(ob) < 3:
                    continue
                ox = float(np.mean([o[1] for o in ob[-3:]]))
                oy = float(np.mean([o[2] for o in ob[-3:]]))
                if hid not in self.cleared and (1.0 if oy >= 0 else -1.0) != self.side0[hid] \
                        and abs(oy) > self.clear_dist:
                    self.cleared.add(hid)
                ahead = robot_x - ox
                if hid in self.cleared or not (-0.5 <= ahead <= self.engage_dist):
                    continue
                p, action, why = None, "go", ""
                known = self.knowledge.get(hid)
                at_deadline = ahead <= self.ask_dist
                waiting = hid in self.asked and known is None and t - self.asked[hid] < self.answer_timeout

                if hid in self.yield_expired:
                    action, why = (("stop", "yield timeout: cautious") if abs(oy) < self.caution_dist
                                   else ("go", "yield timeout: pedestrian away from the line"))
                elif known is not None:
                    action, why = ("stop", "answer: crossing") if known == "crossing" \
                        else ("go", "answer: not crossing")
                else:
                    p = self.predict(hid)
                    a = self.assigned.get(hid)
                    if p is None:
                        action, why = "stop", "not enough history"
                    elif a is None:
                        if not at_deadline:
                            why = "observing until the deadline"
                        else:
                            if self.request is None:
                                self.request = (hid, p)
                            self.held_steps += 1
                            action, why = "stop", "waiting for epoch"
                    elif a == ASK:
                        if hid not in self.asked:
                            self.asked[hid] = t
                            self.asks.append(dict(t=round(t, 3), human=hid))
                            to_ask.append(hid)
                            action, why = "stop", "fleet: asked"
                        elif waiting:
                            action, why = "stop", "fleet: waiting for answer"
                        elif abs(oy) < self.caution_dist:
                            action, why = "stop", "fleet ask, no answer: cautious"
                        else:
                            why = "fleet ask, no answer: pedestrian away from the line"
                    elif a == STOP:
                        action, why = "stop", "fleet: yield"
                    else:  # GO, with the Ask or Act confidence reflex
                        action, why = (("stop", "fleet go, reflex: crossing") if p >= self.p_high
                                       else ("go", "fleet: go"))
                if action == "stop" and why in ("answer: crossing", "fleet: yield",
                                                "fleet go, reflex: crossing"):
                    start = self.yield_start.setdefault(hid, t)
                    if t - start > self.yield_timeout:
                        self.yield_expired.add(hid)
                else:
                    self.yield_start.pop(hid, None)
                self.decisions.append((round(t, 3), hid, "" if p is None else round(p, 4), action, why,
                                       round(ahead, 3), round(abs(oy), 3)))
                if action == "stop":
                    go, reason = False, why
            return go, reason, to_ask

    return FleetPolicy


def run_fleet(labels, policies, noise, shifts, aoa, joint=None, service=1.5,
              window=1.5, answer_accuracy=1.0):
    """Simulate N robots in lockstep.

    labels, policies : one Ask or Act scenario label and policy per robot
    shifts           : integer step offsets c_i; robot i's local step is k = g - c_i
    aoa              : dict with build_trajectory, pose_at, ROBOT, COLLISION_DIST
    joint            : callable(list of p, list of robot indices) -> list of actions,
                       or None for independent policies
    Returns (per-robot result dicts, list of halted global-step sets).
    """
    build_trajectory, pose_at = aoa["build_trajectory"], aoa["pose_at"]
    ROBOT, COLLISION_DIST = aoa["ROBOT"], aoa["COLLISION_DIST"]
    (x0, y0), (xg, yg) = ROBOT["start"], ROBOT["goal"]
    speed = ROBOT["speed"]
    k0, kmax = -int(round(START_DELAY / DT)), int(MAX_DURATION / DT)

    R = []
    for lab, pol, c in zip(labels, policies, shifts):
        traj = build_trajectory(lab["start"], lab["plan"], lab["human_speed"])
        R.append(dict(lab=lab, pol=pol, c=int(c), traj=traj, times=[s[0] for s in traj],
                      rng_obs=random.Random(f"obs-{lab['id']}"),
                      rng_ans=random.Random(f"answers-{lab['id']}"),
                      rx=x0, pending=[], stopped=0.0, min_d=float("inf"),
                      outcome="timed out", t=0.0, done=False, halted=set()))
    busy = -10 ** 9                          # operator busy until (global step)
    service_steps = int(round(service / DT))
    epoch_open = None
    window_steps = int(round(window / DT))
    epochs = []

    for g in range(min(k0 + s["c"] for s in R), max(kmax + s["c"] for s in R) + 1):

        for s in R:
            if s["done"]:
                continue
            k = g - s["c"]
            if k < k0:
                continue
            if k > kmax:
                s["done"] = True
                continue
            t, lab, pol = k * DT, s["lab"], s["pol"]
            s["t"] = t
            hx, hy, _, _ = pose_at(s["traj"], s["times"], t - lab["release_delay"])
            if k % OBS_EVERY == 0:
                pol.add_observation(1, t, hx + s["rng_obs"].gauss(0, noise),
                                    hy + s["rng_obs"].gauss(0, noise))
            if t < 0:
                continue
            for item in [a for a in s["pending"] if a[0] <= t]:
                s["pending"].remove(item)
                pol.receive_answer(item[1], item[2], t)
            rx = s["rx"]
            ry = y0 + (yg - y0) * (x0 - rx) / (x0 - xg)
            s["min_d"] = min(s["min_d"], math.hypot(hx - rx, hy - ry))
            if rx - xg <= 0.15:
                s["outcome"], s["done"] = "reached goal", True
                continue
            if t < lab["robot_delay"]:
                continue
            go, _, to_ask = pol.decide(t, rx)
            for hid in to_ask:
                if s["rng_ans"].random() < 1.0:          # response_prob = 1, as in simulate()
                    wrong = "not_crossing" if lab["intent"] == "crossing" else "crossing"
                    ans = lab["intent"] if s["rng_ans"].random() < answer_accuracy else wrong
                    # operator clock in integer steps; with no wait the answer time is
                    # exactly t + service, as in simulate()
                    wait = max(0, busy - g)
                    busy = g + wait + service_steps
                    s["pending"].append((t + wait * DT + service if wait else t + service, hid, ans))
            if go:
                s["rx"] = rx - speed * DT
            else:
                s["stopped"] += DT
                s["halted"].add(g)

        if joint is not None:
            waiting = [i for i, s in enumerate(R) if s["pol"].request is not None
                       and s["pol"].request[0] not in s["pol"].assigned]
            if waiting and epoch_open is None:
                epoch_open = g
            if epoch_open is not None:
                approaching = [s for s in R if s["pol"].request is None and not s["done"]]
                if not approaching or g - epoch_open >= window_steps:
                    ps = [R[i]["pol"].request[1] for i in waiting]
                    acts = joint(ps, waiting)
                    for i, a in zip(waiting, acts):
                        R[i]["pol"].assigned[R[i]["pol"].request[0]] = int(a)
                    epochs.append(dict(size=len(waiting), held_s=(g - epoch_open) * DT))
                    epoch_open = None
        if all(s["done"] for s in R):
            break

    out = []
    for s in R:
        lab, pol = s["lab"], s["pol"]
        free_time = lab["robot_delay"] + (x0 - xg - 0.15) / speed
        whys = [d[4] for d in pol.decisions]
        out.append(dict(
            outcome=s["outcome"], duration=round(s["t"], 3), delay=round(s["t"] - free_time, 3),
            min_dist=round(s["min_d"], 3), collision=s["min_d"] < COLLISION_DIST,
            n_asks=len(pol.asks), stopped_time=round(s["stopped"], 3),
            fallback=any("no answer" in w for w in whys),
            held_s=round(getattr(pol, "held_steps", 0) * DT, 3),
            action=getattr(pol, "assigned", {}).get(1, -1)))
    return out, [s["halted"] for s in R], epochs


def congestion_time(halted, pairs) -> float:
    """Seconds during which both robots of a neighbouring pair were halted."""
    return sum(len(halted[i] & halted[j]) for i, j in pairs) * DT


# --------------------------------------------------------------------------- #
# Fast prediction: the same pipeline (StandardScaler -> MLP -> calibrator) evaluated in numpy.
# sklearn's per-call input validation dominated simulation time; tests check equality.
# --------------------------------------------------------------------------- #
_FAST = {}


def _fast_parts(model, calibrator):
    import numpy as np
    key = (id(model), id(calibrator))
    if key in _FAST:
        return _FAST[key]
    parts = None
    try:
        scaler, mlp = model.steps[0][1], model.steps[-1][1]
        if (type(scaler).__name__ == "StandardScaler" and type(mlp).__name__ == "MLPClassifier"
                and mlp.activation == "relu" and mlp.out_activation_ == "logistic" and len(model.steps) == 2):
            parts = dict(mean=scaler.mean_, scale=scaler.scale_, W=mlp.coefs_, b=mlp.intercepts_)
    except (AttributeError, IndexError):
        parts = None
    cal = None
    if calibrator is not None and type(calibrator).__name__ == "IsotonicCalibrator":
        iso = calibrator.iso
        # scikit-learn >= 0.24 stores X_thresholds_; 0.23 (the Ask or Act Gazebo machine) _necessary_X_
        x = getattr(iso, "X_thresholds_", getattr(iso, "_necessary_X_", None))
        y = getattr(iso, "y_thresholds_", getattr(iso, "_necessary_y_", None))
        if (x is not None and y is not None and getattr(iso, "out_of_bounds", "") == "clip"
                and getattr(iso, "increasing_", True) is not False):
            cal = ("iso", np.asarray(x, float), np.asarray(y, float))
    _FAST[key] = (parts, cal)
    return _FAST[key]


def _fast_probability(model, calibrator, f):
    import numpy as np
    parts, cal = _fast_parts(model, calibrator)
    if parts is None:
        p = float(model.predict_proba(f.reshape(1, -1))[0, 1])
    else:
        h = (np.asarray(f, float) - parts["mean"]) / parts["scale"]
        for W, b in zip(parts["W"][:-1], parts["b"][:-1]):
            h = np.maximum(h @ W + b, 0.0)
        z = float((h @ parts["W"][-1] + parts["b"][-1])[0])
        p = 1.0 / (1.0 + np.exp(-z))
    if calibrator is None:
        return float(p)
    if cal is not None:
        _, x, y = cal
        return float(np.clip(np.interp(p, x, y), 1e-6, 1 - 1e-6))
    return float(calibrator.transform(np.array([p]))[0])
