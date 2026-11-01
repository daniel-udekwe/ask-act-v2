"""QAOA on the queue formulation against the budget ablation (development seeds only).

Instances: N robots drawn from the development pool (noisy tracking, decision-aware
calibration). Formulations on the same probabilities:
  queue            no budget, q = 1.5 per pair of askers          (2N qubits)
  budget_slack     B = ceil(N/3), slack bits                      (2N + K qubits)
  budget_unbal     B = ceil(N/3), unbalanced penalization          (2N qubits)
Each is compared with its own exact optimum. Optional noisy pass: the trained
circuits sampled under the ibm_kingston noise model.

Usage: python scripts/queue_qaoa.py [--sizes 4 6 8] [--instances 8] [--noisy]
Writes results/queue_qaoa.csv (appends rows when --append).
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from fleet_qubo.pool import ScenarioPool  # noqa: E402
from fleet_qubo.qubo import build_qubo  # noqa: E402
from fleet_qubo.qaoa import QaoaProblem, optimise, interp, evaluate, qiskit_circuit  # noqa: E402
from fleet_qubo.instances import default_budget  # noqa: E402

COST = dict(C=100.0, tau_s=10.0, tau_a=1.5, kappa=0.5)
SEED = 4_400_000


def formulations(pool, N, k):
    scen = pool.draw("noisy", N, np.random.default_rng([SEED + k, N]))
    up = json.load(open(os.path.join(ROOT, "results", "up_weights.json")))
    base = lambda **kw: pool.instance("noisy", scen, "isotonic_dw", **COST, **kw)
    q_inst = base(B=N)
    q_inst.q = 1.5
    b_inst = base(B=default_budget(N))
    return [("queue", q_inst, "slack", None),
            ("budget_slack", b_inst, "slack", None),
            ("budget_unbal", b_inst, "unbalanced", {"lam_1": up["lam_1"], "lam_2": up["lam_2"]})]


def counts_metrics(counts, prob):
    keys = np.array([int(x.replace(" ", ""), 2) for x in counts])
    w = np.array(list(counts.values()), dtype=float)
    w /= w.sum()
    feas = prob.state_feas[keys]
    return {"p_opt": float(w[prob.state_opt[keys]].sum()), "p_feasible": float(w[feas].sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[4, 6, 8])
    ap.add_argument("--instances", type=int, default=8)
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--noisy", action="store_true")
    ap.add_argument("--shots", type=int, default=2000)
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "queue_qaoa.csv"))
    a = ap.parse_args()
    pool = ScenarioPool(os.path.join(ROOT, "results", "deadline_probs.csv"))
    rows = pd.read_csv(a.out).to_dict("records") if a.append and os.path.exists(a.out) else []
    if a.noisy:
        from qiskit import transpile
        from qiskit_aer import AerSimulator
        from qiskit_ibm_runtime.fake_provider import FakeKingston
        backend = FakeKingston()
        sim = AerSimulator.from_backend(backend)
    for N in a.sizes:
        for k in range(a.instances):
            for name, inst, enc, pen in formulations(pool, N, k):
                prob = QaoaProblem(build_qubo(inst, enc, pen), inst)
                params = None
                for p in range(1, a.max_depth + 1):
                    t0 = time.perf_counter()
                    params, _ = optimise(prob, p, init=interp(params) if params is not None else None,
                                         restarts=3, seed=SEED + k)
                    m = evaluate(params, prob, shots=1024, seed=k)
                    row = dict(N=N, instance=k, formulation=name, depth=p, qubits=prob.n,
                               ground_state_ok=prob.ground_state_ok, sim="noiseless",
                               p_opt=m["p_opt"], p_feasible=m["p_feasible"],
                               random_p_opt=m["random_p_opt"], random_p_feasible=m["random_p_feasible"],
                               expected_feasible_cost=m["expected_feasible_cost"], opt_cost=prob.opt_cost)
                    if a.noisy:
                        qc = transpile(qiskit_circuit(prob, params, measure=True), backend,
                                       optimization_level=3, seed_transpiler=0)
                        counts = sim.run(qc, shots=a.shots, seed_simulator=k).result().get_counts()
                        row.update(sim="kingston_noise", cz_gates=qc.count_ops().get("cz", 0),
                                   noiseless_p_opt=m["p_opt"], noiseless_p_feasible=m["p_feasible"],
                                   **counts_metrics(counts, prob))
                    row["secs"] = round(time.perf_counter() - t0, 1)
                    rows.append(row)
                    print(N, k, name, p, prob.n, round(row["p_opt"], 4), round(row["p_feasible"], 3),
                          row["secs"], flush=True)
            pd.DataFrame(rows).to_csv(a.out, index=False)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
