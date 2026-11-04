"""Final QAOA benchmark for H2 (ANALYSIS_PLAN.md section 6). Run only after the v2-prereg tag.

Queue formulation, kappa = 1.5, q = 1.5, noisy tracking, decision-aware calibration.
20 instances per N in {4, 6, 8} from the final pool (instance seeds 8 200 000 + k).
Vanilla QAOA, INTERP depth growth to depth 3, 3 restarts (as in development).
Probabilities are exact (noiseless statevector); 1,024 shots are drawn for the best-sample gap.

H2 per instance: lift = P(optimum) / uniform-random P(optimum) >= 10, and the expected cost over
feasible QAOA samples < the expected cost of a uniformly random feasible bitstring.

Usage: python scripts/final_qaoa.py [--pool ...] [--seed ...] [--instances 20] [--out ...]
Resumable per (N, instance).
"""
import argparse
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import qaoa_variants as qv  # noqa: E402
from fleet_qubo.pool import ScenarioPool  # noqa: E402
from fleet_qubo.qubo import build_qubo  # noqa: E402
from fleet_qubo.instances import true_cost  # noqa: E402
from fleet_qubo.qaoa import QaoaProblem, optimise, interp  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=os.path.join(ROOT, "results", "final", "deadline_probs.csv"))
    ap.add_argument("--seed", type=int, default=8_200_000)
    ap.add_argument("--sizes", type=int, nargs="+", default=[4, 6, 8])
    ap.add_argument("--instances", type=int, default=20)
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--restarts", type=int, default=3)
    ap.add_argument("--shots", type=int, default=1024)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "final", "qaoa_h2.csv"))
    a = ap.parse_args()
    qv.SEED = a.seed                                   # instance(pool, N, k) draws with SEED + k
    pool = ScenarioPool(a.pool)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    rows = pd.read_csv(a.out).to_dict("records") if os.path.exists(a.out) else []
    done = {(r["N"], r["instance"]) for r in rows}
    for N in a.sizes:
        for k in range(a.instances):
            if (N, k) in done:
                continue
            t0 = time.perf_counter()
            inst = qv.instance(pool, N, k)
            prob = QaoaProblem(build_qubo(inst, "slack"), inst)
            _, acts = qv.heuristic_bits(inst)
            heur = true_cost(inst, acts)
            params = None
            for p in range(1, a.depth + 1):
                params, _ = optimise(prob, p, init=interp(params) if params is not None else None,
                                     restarts=a.restarts, seed=a.seed + k)
            m = qv.metrics(params, prob, None, heur, a.shots, k)
            feas = prob.state_feas
            rand_cost = float(prob.state_cost[feas].mean())
            rand_gap = (rand_cost - prob.opt_cost) / abs(prob.opt_cost)
            lift = m["p_opt"] / m["random_p_opt"]
            rows.append(dict(N=N, instance=k, depth=a.depth, qubits=prob.n, opt_cost=prob.opt_cost,
                             ground_state_ok=prob.ground_state_ok, lift=lift, random_feasible_gap=rand_gap,
                             h2_pass=bool(lift >= 10 and m["feasible_cost_gap"] < rand_gap),
                             secs=round(time.perf_counter() - t0, 1), params=list(np.round(params, 5)), **m))
            print(N, k, round(lift, 1), round(m["feasible_cost_gap"], 3), round(rand_gap, 3),
                  rows[-1]["h2_pass"], rows[-1]["secs"], flush=True)
            pd.DataFrame(rows).to_csv(a.out, index=False)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
