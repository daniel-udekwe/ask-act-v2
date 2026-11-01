"""Month 5: QAOA variants on the queue formulation (development seeds only).

Variants, all with INTERP depth growth and the same restart budget:
  vanilla   standard QAOA (|+> start, X mixer), expectation objective
  warm      warm start from the per-robot heuristic (each robot's own optimum, ignoring
            the queue), regularised to c = 0.25 / 0.75 (Egger et al. 2021)
  cvar      standard circuit, CVaR objective with alpha = 0.1 (Barkoutsos et al. 2020)

Cost model: C = 100, tau_s = 10, tau_a = 1.5, kappa = 1.5 (primary), q = 1.5 per pair of askers.
Instances: noisy tracking, decision-aware calibration, development pool.

Usage: python scripts/qaoa_variants.py --sizes 4 6 8 --instances 6 [--restarts 3] [--out ...]
"""
import argparse
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from fleet_qubo.pool import ScenarioPool  # noqa: E402
from fleet_qubo.qubo import build_qubo  # noqa: E402
from fleet_qubo.instances import GO, STOP, ASK, true_cost  # noqa: E402
from fleet_qubo.qaoa import (QaoaProblem, optimise, interp, qaoa_state, warm_from_bits)  # noqa: E402

COST = dict(C=100.0, tau_s=10.0, tau_a=1.5, kappa=1.5)
Q = 1.5
SEED = 4_500_000
VARIANTS = {"vanilla": dict(cvar=None, warm=False), "warm": dict(cvar=None, warm=True),
            "cvar": dict(cvar=0.1, warm=False)}


def instance(pool, N, k):
    scen = pool.draw("noisy", N, np.random.default_rng([SEED + k, N]))
    inst = pool.instance("noisy", scen, "isotonic_dw", B=N, **COST)
    inst.q = Q
    return inst


def heuristic_bits(inst):
    """Each robot's own optimum, ignoring the queue: bits (a_0..a_{N-1}, s_0..s_{N-1})."""
    acts = inst.unary_costs().argmin(axis=1)
    return np.concatenate([(acts == ASK).astype(int), (acts == STOP).astype(int)]), acts


def metrics(params, prob, warm, heur_cost, shots, seed):
    probs = np.abs(qaoa_state(params, prob, warm)) ** 2
    probs /= probs.sum()
    feas = prob.state_feas
    cost = prob.state_cost
    p_feas = float(probs[feas].sum())
    exp_cost = float(probs[feas] @ cost[feas]) / p_feas
    rng = np.random.default_rng(seed)
    s = rng.choice(len(probs), size=shots, p=probs)
    best = cost[s][feas[s]].min() if feas[s].any() else np.inf
    return dict(p_opt=float(probs[prob.state_opt].sum()), random_p_opt=float(prob.state_opt.mean()),
                p_feasible=p_feas, feasible_cost_gap=(exp_cost - prob.opt_cost) / abs(prob.opt_cost),
                p_beats_heuristic=float(probs[feas & (cost < heur_cost - 1e-9)].sum()),
                best_sample_gap=(best - prob.opt_cost) / abs(prob.opt_cost))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[4, 6, 8])
    ap.add_argument("--instances", type=int, default=6)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--restarts", type=int, default=3)
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "qaoa_variants.csv"))
    a = ap.parse_args()
    pool = ScenarioPool(os.path.join(ROOT, "results", "deadline_probs.csv"))
    rows = []
    for N in a.sizes:
        for k in range(a.instances):
            inst = instance(pool, N, k)
            prob = QaoaProblem(build_qubo(inst, "slack"), inst)
            bits, acts = heuristic_bits(inst)
            heur_cost = true_cost(inst, acts)
            for name, v in VARIANTS.items():
                warm = warm_from_bits(bits, 0.25) if v["warm"] else None
                params = None
                for p in range(1, a.max_depth + 1):
                    t0 = time.perf_counter()
                    params, _ = optimise(prob, p, init=interp(params) if params is not None else None,
                                         cvar=v["cvar"], restarts=a.restarts, seed=SEED + k, warm=warm)
                    m = metrics(params, prob, warm, heur_cost, a.shots, k)
                    rows.append(dict(N=N, instance=k, variant=name, depth=p, qubits=prob.n,
                                     opt_cost=prob.opt_cost, heuristic_gap=(heur_cost - prob.opt_cost) / abs(prob.opt_cost),
                                     ground_state_ok=prob.ground_state_ok, secs=round(time.perf_counter() - t0, 1),
                                     params=list(np.round(params, 5)), **m))
                    print(N, k, name, p, round(m["p_opt"], 4), round(m["p_feasible"], 3),
                          round(m["feasible_cost_gap"], 3), rows[-1]["secs"], flush=True)
            pd.DataFrame(rows).to_csv(a.out, index=False)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
