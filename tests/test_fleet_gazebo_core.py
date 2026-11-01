"""The Gazebo coordinator's rules must reproduce the offline simulator exactly.

`drive` below is the Gazebo pipeline without ROS: each robot runs the same per-step code as
fleet_sim.run_fleet, but questions go through coordinator_core.Operator and deadline
requests through coordinator_core.Epochs, the way fleet_controller.py and
fleet_coordinator.py exchange them. Its outcomes must equal run_fleet's.
"""
import math
import os
import py_compile
import random
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fleet_gazebo"))
from coordinator_core import Operator, Epochs  # noqa: E402

AOA = os.environ.get("AOA_REPO", "/home/claude/daniel-udekwe/turtlebot3-ask_or_act")
MODEL = os.environ.get("AOA_MODEL", "/home/claude/aoa_data/predictor/intent_model.pkl")
POOL = os.path.join(ROOT, "results", "deadline_probs.csv")
need_aoa = pytest.mark.skipif(not (os.path.isdir(AOA) and os.path.exists(MODEL) and os.path.exists(POOL)),
                              reason="needs the Ask or Act repository, a trained model and the pool")


def test_operator_first_come_first_served():
    op = Operator(service=1.5)
    times = [op.ask(t, r, f"s{r}", "crossing")[0] for r, t in enumerate([0.0, 0.5, 4.0, 4.1])]
    assert times == pytest.approx([1.5, 3.0, 5.5, 7.0])


def test_operator_answers_follow_scenario_stream():
    op = Operator(service=1.5, answer_accuracy=0.5)
    answers = [op.ask(0.0, 0, "cafe_hs_x_4001", "crossing")[1] for _ in range(20)]
    rng = random.Random("answers-cafe_hs_x_4001")
    expect = []
    for _ in range(20):
        rng.random()
        expect.append("crossing" if rng.random() < 0.5 else "not_crossing")
    assert answers == expect


def test_epoch_closes_when_all_arrive_or_window_passes():
    seen = []
    ep = Epochs(3, lambda ps, idx: (seen.append(idx), [2] * len(ps))[1], window=1.5)
    ep.request(1.0, 0, 0.5)
    assert ep.tick(1.0) == {}
    ep.request(1.2, 2, 0.4)
    assert ep.tick(1.2) == {}
    ep.finish(1)                                         # robot 1 finished without a request
    assert ep.tick(1.25) == {0: 2, 2: 2}
    ep2 = Epochs(2, lambda ps, idx: [0] * len(ps), window=1.5)
    ep2.request(0.0, 0, 0.1)
    assert ep2.tick(1.45) == {}
    assert ep2.tick(1.5) == {0: 0}                       # window reached, robot 1 still approaching


def test_ros_scripts_compile():
    for f in ("fleet_controller.py", "fleet_pedestrians.py", "fleet_coordinator.py",
              "run_fleet_gazebo.py", "compare_fleet_validation.py", "epochs.py"):
        py_compile.compile(os.path.join(ROOT, "fleet_gazebo", f), doraise=True)


def drive(labels, pols, noise, shifts, env, solve, DT=0.05):
    """run_fleet's loop, with the operator and epochs delegated to coordinator_core."""
    from fleet_qubo.fleet_sim import START_DELAY, MAX_DURATION, OBS_EVERY
    ROBOT = env["ROBOT"]
    (x0, y0), (xg, yg) = ROBOT["start"], ROBOT["goal"]
    k0, kmax = -int(round(START_DELAY / DT)), int(MAX_DURATION / DT)
    op = Operator(1.5)
    ep = Epochs(len(labels), solve, 1.5) if solve else None
    R = []
    for lab, pol, c in zip(labels, pols, shifts):
        traj = env["build_trajectory"](lab["start"], lab["plan"], lab["human_speed"])
        R.append(dict(lab=lab, pol=pol, c=c, traj=traj, times=[s[0] for s in traj],
                      rng=random.Random(f"obs-{lab['id']}"), rx=x0, pending=[], min_d=math.inf,
                      done=False, sent=False, asks=0))
    for g in range(min(k0 + s["c"] for s in R), max(kmax + s["c"] for s in R) + 1):
        for i, s in enumerate(R):
            if s["done"]:
                continue
            k = g - s["c"]
            if k < k0:
                continue
            if k > kmax:
                s["done"] = True
                ep and ep.finish(i)
                continue
            t, lab, pol = k * DT, s["lab"], s["pol"]
            hx, hy, _, _ = env["pose_at"](s["traj"], s["times"], t - lab["release_delay"])
            if k % OBS_EVERY == 0:
                pol.add_observation(1, t, hx + s["rng"].gauss(0, noise), hy + s["rng"].gauss(0, noise))
            if t < 0:
                continue
            for item in [a for a in s["pending"] if a[0] <= t + 1e-9]:
                s["pending"].remove(item)
                pol.receive_answer(item[1], item[2], t)
            ry = y0 + (yg - y0) * (x0 - s["rx"]) / (x0 - xg)
            s["min_d"] = min(s["min_d"], math.hypot(hx - s["rx"], hy - ry))
            if s["rx"] - xg <= 0.15:
                s["done"] = True
                ep and ep.finish(i)
                continue
            if t < lab["robot_delay"]:
                continue
            go, _, to_ask = pol.decide(t, s["rx"])
            if ep and pol.request is not None and not s["sent"]:
                ep.request(g * DT, i, pol.request[1])
                s["sent"] = True
            for hid in to_ask:
                t_ans, ans = op.ask(g * DT, i, lab["id"], lab["intent"])
                s["pending"].append((t_ans - s["c"] * DT, hid, ans))
            if go:
                s["rx"] -= ROBOT["speed"] * DT
        if ep:
            for i, a in ep.tick(g * DT).items():
                R[i]["pol"].assigned[R[i]["pol"].request[0]] = a
        if all(s["done"] for s in R):
            break
    return [dict(collision=s["min_d"] < env["COLLISION_DIST"], n_asks=len(s["pol"].asks)) for s in R]


@need_aoa
@pytest.mark.parametrize("mode", ["independent", "joint"])
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_coordinator_pipeline_matches_offline(mode, seed):
    sys.path.insert(0, AOA)
    sys.path.insert(0, ROOT)
    import generate_scenarios as gs
    import ped_traj
    import policy as aoa_policy
    import simulate_policies as sp
    from fleet_qubo.fleet_sim import run_fleet, make_policy_class
    from fleet_qubo.instances import Instance
    from fleet_qubo.classical import exhaustive
    from epochs import build_epoch, band

    FP = make_policy_class(aoa_policy.AskOrActPolicy)
    env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at,
               ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
    labels, shifts = build_epoch(POOL, "noisy", 4, 4_800_000 + seed)
    model, cal = aoa_policy.load_predictor(MODEL, "mlp", "isotonic_dw", "noisy")
    lo, hi = band(1.5)

    def solve(ps, idx):
        return exhaustive(Instance(p=np.array(ps), B=len(ps), q=1.5, C=100.0, tau_s=10.0,
                                   tau_a=1.5, kappa=1.5))["actions"]

    mk = lambda: [FP(model, cal, mode=mode, true_intent=l["intent"], p_low=lo, p_high=hi) for l in labels]
    noise = gs.CONDITIONS["noisy"]["noise"]
    ref, _, _ = run_fleet(labels, mk(), noise, shifts, env, joint=solve if mode == "joint" else None)
    got = drive(labels, mk(), noise, shifts, env, solve if mode == "joint" else None)
    assert [r["collision"] for r in got] == [r["collision"] for r in ref]
    assert [r["n_asks"] for r in got] == [r["n_asks"] for r in ref]
