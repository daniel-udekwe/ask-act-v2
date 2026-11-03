"""Month-3 closed-loop study (development seeds only).

N robots, each with an Ask or Act scenario from the development pool, reach their
decision deadlines within a `jitter`-second window. One operator answers questions
one at a time (1.5 s each). Methods, all paired on the same scenarios and timing:

  independent   unchanged Ask or Act policy (fixed band), shared operator
  joint_none    exact joint solver, budget coupling only
  joint_single  exact joint solver, budget + single-corridor congestion coupling

Cost model: C = 100, tau_s = 10, tau_a + kappa = 2, B = ceil(N/3).
Usage: python scripts/closed_loop.py [--epochs 200] [--N 6] [--workers 2]
Writes results/closed_loop.csv.
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
MODEL = os.environ.get("AOA_MODEL", os.path.join(ROOT, "predictor", "intent_model.pkl"))
sys.path.insert(0, AOA)

from fleet_qubo.instances import Instance, corridor_edges, default_budget  # noqa: E402
from fleet_qubo.classical import exhaustive  # noqa: E402
from fleet_qubo.fleet_sim import run_fleet, make_policy_class, congestion_time, DT  # noqa: E402

COST = dict(C=100.0, tau_s=10.0, tau_a=1.5, kappa=0.5)
QUEUE_COST = 1.5   # one 1.5 s service time of waiting per pair of askers, at 1 cost unit per second
METHODS = os.environ.get("METHODS", "independent,joint_none,joint_single").split(",")
# independent_costband: each robot applies the C = 100 rule alone (go below p = 0.02)
BANDS = {"independent": (0.2, 0.8), "independent_costband": (0.02, 0.8)}
CALS = {"raw": ("raw", None), "isotonic": ("isotonic", True), "isotonic_dw": ("isotonic_dw", True)}
EPOCH_SEED = 4_200_000          # development epoch block (scenario pool 4000-4099)


def joint_solver(variant, N):
    """variant: none / single (hard budget B), or queue (no budget; q per pair of askers)."""
    # free: no coupling at all (each robot's own optimum at the deadline, no early commits)
    layout = "none" if variant in ("queue", "free") else variant
    B = N if variant in ("queue", "free") else default_budget(N)
    q = QUEUE_COST if variant == "queue" else 0.0

    def solve(ps, idx):
        m = len(ps)
        Ec, En = corridor_edges(N, layout)
        pos = {r: j for j, r in enumerate(idx)}
        Ec = {(pos[i], pos[j]): w for (i, j), w in Ec.items() if i in pos and j in pos}
        inst = Instance(p=np.array(ps), B=B, Ec=Ec, En={}, q=q, **COST)
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
    kind, recal = CALS[cal]
    model, calib = aoa_policy.load_predictor(MODEL, "mlp", kind, cond if recal else "nominal")
    pool = pd.read_csv(os.path.join(ROOT, "results", "deadline_probs.csv"))
    pool = pool[(pool.condition == cond) & pool.reached_deadline & (pool.calibration == "isotonic_dw")]
    pool = pool.drop_duplicates("scenario").reset_index(drop=True)
    pairs = list(corridor_edges(N, "single")[0])
    rows = []
    for e in epochs:
        rng = np.random.default_rng([EPOCH_SEED + e, N])
        pick = pool.iloc[rng.choice(len(pool), size=N, replace=False)]
        u = rng.uniform(0, jitter, size=N)
        labs = [gs.build("cafe", r.family, r.intent, int(r.seed), cond) for r in pick.itertuples()]
        shifts = [int(round((ui - td) / DT)) for ui, td in zip(u, pick.t_deadline)]
        for method in METHODS:
            mode = "independent" if method.startswith("independent") else "joint"
            lo, hi = BANDS.get(method, (0.2, 0.8))
            pols = [FleetPolicy(model, calib, mode=mode, true_intent=l["intent"], p_low=lo, p_high=hi)
                    for l in labs]
            joint = None if mode == "independent" else joint_solver(method.split("_")[1], N)
            out, halted, ep = run_fleet(labs, pols, gs.CONDITIONS[cond]["noise"], shifts, env, joint=joint)
            cong = congestion_time(halted, pairs)
            for i, (o, l) in enumerate(zip(out, labs)):
                rows.append(dict(condition=cond, calibration=cal, method=method, N=N, epoch=e, robot=i,
                                 scenario=l["id"], family=pick.family.iloc[i],
                                 crossing=int(l["intent"] == "crossing"), epoch_congestion_s=cong,
                                 epochs_in_episode=len(ep), **o))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--N", type=int, default=6)
    ap.add_argument("--jitter", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--chunks", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "closed_loop.csv.gz"))
    a = ap.parse_args()
    ep = np.array_split(np.arange(a.epochs), a.chunks)
    jobs = [(c, k, list(e), a.N, a.jitter) for c, k, e in
            itertools.product(["nominal", "noisy"], CALS, ep)]
    t0, rows = time.time(), []
    with Pool(a.workers) as p:
        for i, r in enumerate(p.imap_unordered(task, jobs)):
            rows += r
            print(f"{i + 1}/{len(jobs)} jobs, {time.time() - t0:.0f} s", flush=True)
    pd.DataFrame(rows).to_csv(a.out, index=False)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
