"""Month-4 Pareto study: operator load against safety and delay (development seeds only).

Two families of policies, each swept over the operator cost per question kappa:

  indep_k<kappa>       each robot applies its own cost-model optimum (no coordination),
                       i.e. the band  ask cost / C  <  p  <  1 - ask cost / tau_s,
                       with early confident commits, sharing one serial operator
  jq_k<kappa>_q<q>     queue-aware joint solver (exact), all robots held to the epoch

plus a q sweep at kappa = 0.5. Ask cost = tau_a + kappa, tau_a = 1.5, C = 100, tau_s = 10.
Paired: every method sees the same scenarios, timing, noise and answers per epoch.

Usage: python scripts/pareto.py [--epochs 500] [--workers 2]
Writes results/pareto.csv (one row per robot).
"""
import argparse
import itertools
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
AOA = os.environ.get("AOA_REPO", "/home/claude/daniel-udekwe/turtlebot3-ask_or_act")
MODEL = os.environ.get("AOA_MODEL", "/home/claude/aoa_data/predictor/intent_model.pkl")
sys.path.insert(0, AOA)

from fleet_qubo.instances import Instance  # noqa: E402
from fleet_qubo.classical import exhaustive  # noqa: E402
from fleet_qubo.fleet_sim import run_fleet, make_policy_class, DT  # noqa: E402

C, TAU_S, TAU_A = 100.0, 10.0, 1.5
KAPPAS = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
QS = [0.0, 0.75, 1.5, 3.0, 6.0]
EPOCH_SEED = 4_300_000            # development epoch block (scenario pool 4000-4099)


def methods():
    m = [("indep", k, 0.0) for k in KAPPAS]
    m += [("jq", k, 1.5) for k in KAPPAS]
    m += [("jq", 0.5, q) for q in QS if q != 1.5]
    return m


def band(kappa):
    ask = TAU_A + kappa
    lo = min(ask / C, TAU_S / (C + TAU_S))          # go below this
    hi = max(1.0 - ask / TAU_S, TAU_S / (C + TAU_S))  # stop above this
    return lo, hi


def joint(kappa, q):
    def solve(ps, idx):
        inst = Instance(p=np.array(ps), B=len(ps), q=q, C=C, tau_s=TAU_S, tau_a=TAU_A, kappa=kappa)
        return exhaustive(inst)["actions"]
    return solve


def task(args):
    cond, cal, epochs, N, jitter = args
    import generate_scenarios as gs
    import ped_traj
    import policy as aoa_policy
    import simulate_policies as sp
    FleetPolicy = make_policy_class(aoa_policy.AskOrActPolicy)
    env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at,
               ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
    model, calib = aoa_policy.load_predictor(MODEL, "mlp", cal, cond)
    pool = pd.read_csv(os.path.join(ROOT, "results", "deadline_probs.csv"))
    pool = pool[(pool.condition == cond) & pool.reached_deadline & (pool.calibration == "isotonic_dw")]
    pool = pool.drop_duplicates("scenario").reset_index(drop=True)
    rows = []
    for e in epochs:
        rng = np.random.default_rng([EPOCH_SEED + e, N])
        pick = pool.iloc[rng.choice(len(pool), size=N, replace=False)]
        u = rng.uniform(0, jitter, size=N)
        labs = [gs.build("cafe", r.family, r.intent, int(r.seed), cond) for r in pick.itertuples()]
        shifts = [int(round((ui - td) / DT)) for ui, td in zip(u, pick.t_deadline)]
        for kind, kappa, q in methods():
            if kind == "indep":
                lo, hi = band(kappa)
                pols = [FleetPolicy(model, calib, mode="independent", true_intent=l["intent"],
                                    p_low=lo, p_high=hi) for l in labs]
                out, _, _ = run_fleet(labs, pols, gs.CONDITIONS[cond]["noise"], shifts, env)
            else:
                pols = [FleetPolicy(model, calib, mode="joint", true_intent=l["intent"]) for l in labs]
                out, _, _ = run_fleet(labs, pols, gs.CONDITIONS[cond]["noise"], shifts, env,
                                      joint=joint(kappa, q))
            for i, (o, l) in enumerate(zip(out, labs)):
                rows.append(dict(condition=cond, calibration=cal, N=N, epoch=e, robot=i, kind=kind,
                                 kappa=kappa, q=q, crossing=int(l["intent"] == "crossing"),
                                 collision=int(o["collision"]), n_asks=o["n_asks"], delay=o["delay"],
                                 fallback=int(o["fallback"]), stopped_time=o["stopped_time"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--sizes", type=int, nargs="+", default=[6, 8])
    ap.add_argument("--jitter", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--chunks", type=int, default=5)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "pareto.csv.gz"))
    a = ap.parse_args()
    ep = np.array_split(np.arange(a.epochs), a.chunks)
    jobs = [(c, k, list(e), N, a.jitter) for N, c, k, e in
            itertools.product(a.sizes, ["noisy", "nominal"], ["isotonic", "isotonic_dw"], ep)]
    t0, rows = time.time(), []
    with Pool(a.workers) as p:
        for i, r in enumerate(p.imap_unordered(task, jobs)):
            rows += r
            print(f"{i + 1}/{len(jobs)} jobs, {time.time() - t0:.0f} s", flush=True)
            pd.DataFrame(rows).to_csv(a.out, index=False)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
