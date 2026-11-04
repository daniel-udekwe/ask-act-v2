"""Final closed-loop evaluation (ANALYSIS_PLAN.md sections 4-7). Run only after the v2-prereg tag.

Two stages, both from the same epochs (seeds 8 100 000 + e) and the final scenario pool:

  confirmatory   N = 6 and 8, noisy tracking, decision-aware calibration:
                 joint and rule_matched (alpha = 1 answers), joint_a and rule_a_matched
                 (alpha = 0.9 answers). Feeds H1a/H1b/H4a/H4b.
  exploratory    N = 6 and 8, nominal and noisy, raw / conventional / decision-aware calibration:
                 every method below. Feeds section 7 (all reported, none confirmatory).

Methods (cost model C = 100, tau_s = 10, tau_a = 1.5; queue q = 1.5 unless stated):

  alpha = 1 answers
    aoa_band          fixed Ask or Act band [0.2, 0.8]
    rule_k<k>         per-robot cost-model band at kappa = k, k in {0.5, 1, 2, ..., 7}
    rule_matched      rule at kappa* (N = 6: 5.95, N = 8: 6.15)
    joint             queue-aware joint solver, kappa = 1.5 (primary)
    joint_k<k>        joint solver at kappa = k, k in {0.5, 1, 2, ..., 7}
    joint_budget      joint solver with a hard budget B = ceil(N/3), no queue term
  alpha = 0.9 answers
    rule_a_k<k>       alpha-aware per-robot band, k in {0.5, 1.5, 3, 4, 5, 6, 6.5}
    rule_a_matched    alpha-aware rule at kappa* (N = 6: 6.04, N = 8: 6.20)
    joint_a           alpha-aware joint solver, kappa = 1.5 (H4)
    joint_a_k<k>      alpha-aware joint solver, k in {0.5, 3, 5}
    joint_misspec     joint solver assuming alpha = 1 (exploratory 8)

Usage:
  python scripts/final_closed_loop.py --stage confirmatory
  python scripts/final_closed_loop.py --stage exploratory
  (--pool, --seed, --epochs and --out exist so the pipeline can be tested on development data.)
Resumable: finished (stage, N, condition, calibration, epoch chunk) jobs are skipped.
"""
import argparse
import itertools
import math
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

from fleet_qubo.instances import Instance  # noqa: E402
from fleet_qubo.classical import exhaustive  # noqa: E402
from fleet_qubo.fleet_sim import run_fleet, make_policy_class, DT  # noqa: E402

C, TAU_S, TAU_A, Q, KAPPA = 100.0, 10.0, 1.5, 1.5, 1.5
ALPHA = 0.9
KAPPA_STAR = {6: 5.95, 8: 6.15}            # results/dev_matching.csv
KAPPA_STAR_A = {6: 6.04, 8: 6.20}          # results/dev_matching_alpha.csv
GRID = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
GRID_A = [0.5, 1.5, 3.0, 4.0, 5.0, 6.0, 6.5]
GRID_JA = [0.5, 3.0, 5.0]


def band(kappa, alpha=1.0):
    """Per-robot cost-model band (go below lo, stop above hi, ask in between)."""
    ask, g_s = TAU_A + kappa, TAU_S / (C + TAU_S)
    if alpha == 1.0:
        return min(ask / C, g_s), max(1.0 - ask / TAU_S, g_s)
    lo, hi = ask / (C * alpha), (TAU_S - ask) / (TAU_S + C * (1 - alpha))
    return (lo, hi) if lo < hi else (g_s, g_s)


def methods(stage, N):
    """(name, kind, kappa, q, B, alpha_model, alpha_answers); kind in {band, rule, joint}."""
    a1 = [("rule_matched", "rule", KAPPA_STAR[N], 0, None, 1.0, 1.0),
          ("joint", "joint", KAPPA, Q, None, 1.0, 1.0)]
    a9 = [("rule_a_matched", "rule", KAPPA_STAR_A[N], 0, None, ALPHA, ALPHA),
          ("joint_a", "joint", KAPPA, Q, None, ALPHA, ALPHA)]
    if stage == "confirmatory":
        return a1 + a9
    m = [("aoa_band", "band", None, 0, None, 1.0, 1.0)] + a1
    m += [(f"rule_k{k:g}", "rule", k, 0, None, 1.0, 1.0) for k in GRID]
    m += [(f"joint_k{k:g}", "joint", k, Q, None, 1.0, 1.0) for k in GRID]
    m += [("joint_budget", "joint", KAPPA, 0.0, math.ceil(N / 3), 1.0, 1.0)]
    m += a9 + [(f"rule_a_k{k:g}", "rule", k, 0, None, ALPHA, ALPHA) for k in GRID_A]
    m += [(f"joint_a_k{k:g}", "joint", k, Q, None, ALPHA, ALPHA) for k in GRID_JA]
    m += [("joint_misspec", "joint", KAPPA, Q, None, 1.0, ALPHA)]
    return m


def solver(kappa, q, B, alpha):
    def solve(ps, idx):
        inst = Instance(p=np.array(ps), B=len(ps) if B is None else B, q=q, C=C, tau_s=TAU_S,
                        tau_a=TAU_A, kappa=kappa, alpha=alpha)
        return exhaustive(inst)["actions"]
    return solve


def task(args):
    stage, cond, cal, epochs, N, pool_path, seed0, jitter = args
    import generate_scenarios as gs
    import ped_traj
    import policy as aoa_policy
    import simulate_policies as sp
    FleetPolicy = make_policy_class(aoa_policy.AskOrActPolicy)
    env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at,
               ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
    model, calib = aoa_policy.load_predictor(MODEL, "mlp", cal, cond)
    pool = pd.read_csv(pool_path)
    pool = pool[(pool.condition == cond) & pool.reached_deadline & (pool.calibration == "isotonic_dw")]
    pool = pool.drop_duplicates("scenario").reset_index(drop=True)
    noise = gs.CONDITIONS[cond]["noise"]
    rows = []
    for e in epochs:
        rng = np.random.default_rng([seed0 + e, N])           # same draw as the development studies
        pick = pool.iloc[rng.choice(len(pool), size=N, replace=False)]
        u = rng.uniform(0, jitter, size=N)
        labs = [gs.build("cafe", r.family, r.intent, int(r.seed), cond) for r in pick.itertuples()]
        shifts = [int(round((ui - td) / DT)) for ui, td in zip(u, pick.t_deadline)]
        for name, kind, kappa, q, B, a_model, a_ans in methods(stage, N):
            if kind == "joint":
                pols = [FleetPolicy(model, calib, mode="joint", true_intent=l["intent"]) for l in labs]
                out, _, _ = run_fleet(labs, pols, noise, shifts, env, joint=solver(kappa, q, B, a_model),
                                      answer_accuracy=a_ans)
            else:
                lo, hi = (0.2, 0.8) if kind == "band" else band(kappa, a_model)
                pols = [FleetPolicy(model, calib, mode="independent", true_intent=l["intent"],
                                    p_low=lo, p_high=hi) for l in labs]
                out, _, _ = run_fleet(labs, pols, noise, shifts, env, answer_accuracy=a_ans)
            for i, (o, l) in enumerate(zip(out, labs)):
                rows.append(dict(stage=stage, N=N, condition=cond, calibration=cal, epoch=e, robot=i,
                                 scenario=l["id"], method=name, kappa=kappa, q=q, alpha=a_ans,
                                 crossing=int(l["intent"] == "crossing"), collision=int(o["collision"]),
                                 n_asks=o["n_asks"], delay=o["delay"], fallback=int(o["fallback"]),
                                 stopped_time=o["stopped_time"], held_s=o["held_s"], action=o["action"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["confirmatory", "exploratory"], required=True)
    ap.add_argument("--pool", default=os.path.join(ROOT, "results", "final", "deadline_probs.csv"))
    ap.add_argument("--seed", type=int, default=8_100_000)
    ap.add_argument("--epochs", type=int, default=1000)
    ap.add_argument("--sizes", type=int, nargs="+", default=[6, 8])
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(ROOT, "results", "final", f"closed_loop_{a.stage}.csv.gz")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if a.stage == "confirmatory":
        cells = [("noisy", "isotonic_dw")]
    else:
        cells = list(itertools.product(["noisy", "nominal"], ["isotonic_dw", "isotonic", "raw"]))
    chunks = [list(range(s, min(s + a.chunk, a.epochs))) for s in range(0, a.epochs, a.chunk)]
    jobs = [(a.stage, c, k, ep, N, a.pool, a.seed, 1.0) for N in a.sizes for (c, k) in cells for ep in chunks]
    rows = []
    if os.path.exists(out):
        old = pd.read_csv(out)
        done = set(zip(old.N, old.condition, old.calibration, old.epoch))
        rows = old.to_dict("records")
        jobs = [j for j in jobs if not all((j[4], j[1], j[2], e) in done for e in j[3])]
    print(f"{a.stage}: {len(jobs)} jobs to run -> {out}", flush=True)
    t0 = time.time()
    with Pool(a.workers) as p:
        for i, r in enumerate(p.imap_unordered(task, jobs)):
            rows += r
            pd.DataFrame(rows).to_csv(out, index=False)
            print(f"{i + 1}/{len(jobs)} jobs, {time.time() - t0:.0f} s", flush=True)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
