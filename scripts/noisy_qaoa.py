"""QAOA under the ibm_kingston noise model (FakeKingston snapshot, Heron r2).

Parameters are optimised noiselessly (exact simulator), then the bound circuits are
transpiled for the backend and sampled on Aer with its noise model. Instances come
from the real-probability pool (noisy tracking, decision-aware calibration, dev seeds).
Writes results/noisy_qaoa.csv.
"""
import itertools
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeKingston

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fleet_qubo.pool import ScenarioPool
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem, optimise, interp, evaluate, qiskit_circuit

# Overridable from the environment so runs can be split and appended:
#   SHOTS=2000 CONFIGS=6:none INSTANCES=1,2 APPEND=results/noisy_qaoa.csv
SHOTS = int(os.environ.get("SHOTS", 4000))
CONFIGS = [(int(c.split(":")[0]), c.split(":")[1])
           for c in os.environ.get("CONFIGS", "4:none,6:none,6:single").split(",")]
INSTANCES = [int(i) for i in os.environ.get("INSTANCES", "0,1,2,3,4,5,6,7").split(",")]
UP = json.load(open("results/up_weights.json"))

backend = FakeKingston()
sim = AerSimulator.from_backend(backend)
pool = ScenarioPool("results/deadline_probs.csv")
rows = pd.read_csv(os.environ["APPEND"]).to_dict("records") if os.environ.get("APPEND") else []


def counts_metrics(counts, prob):
    keys = np.array([int(k.replace(" ", ""), 2) for k in counts])
    w = np.array(list(counts.values()), dtype=float)
    w /= w.sum()
    feas = prob.state_feas[keys]
    best = prob.state_cost[keys][feas].min() if feas.any() else np.inf
    gap = (best - prob.opt_cost) / abs(prob.opt_cost) if np.isfinite(best) else np.inf
    return {"p_opt": float(w[prob.state_opt[keys]].sum()), "p_feasible": float(w[feas].sum()),
            "best_sample_gap": float(gap), "found_opt": bool(gap <= 1e-9)}


for (N, layout), k in itertools.product(CONFIGS, INSTANCES):
    seed = 4100_000 + k
    scen = pool.draw("noisy", N, np.random.default_rng([seed, N]))
    inst = pool.instance("noisy", scen, "isotonic_dw", layout)
    for enc in ["slack", "unbalanced"]:
        pen = {"lam_1": UP["lam_1"], "lam_2": UP["lam_2"]} if enc == "unbalanced" else None
        prob = QaoaProblem(build_qubo(inst, enc, pen), inst)
        params = None
        for p in range(1, int(os.environ.get("MAX_DEPTH", 3)) + 1):
            t0 = time.perf_counter()
            params, _ = optimise(prob, p, init=interp(params) if params is not None else None,
                                 restarts=3, seed=seed)
            ideal = evaluate(params, prob, shots=SHOTS, seed=seed)
            qc = transpile(qiskit_circuit(prob, params, measure=True), backend,
                           optimization_level=3, seed_transpiler=0)
            twoq = qc.count_ops().get("cz", 0)
            counts = sim.run(qc, shots=SHOTS, seed_simulator=seed).result().get_counts()
            noisy = counts_metrics(counts, prob)
            base = dict(N=N, layout=layout, instance=k, encoding=enc, depth=p, qubits=prob.n,
                        two_qubit_gates=twoq, ground_state_ok=prob.ground_state_ok,
                        random_p_opt=float(prob.state_opt.mean()),
                        random_p_feasible=float(prob.state_feas.mean()),
                        secs=round(time.perf_counter() - t0, 1), shots=SHOTS)
            rows.append({**base, "sim": "noiseless", **{m: ideal[m] for m in
                         ("p_opt", "p_feasible", "best_sample_gap", "found_opt")}})
            rows.append({**base, "sim": "kingston_noise", **noisy})
            print(N, layout, k, enc, p, twoq, round(ideal["p_opt"], 4), round(noisy["p_opt"], 4),
                  round(noisy["p_feasible"], 3), base["secs"], flush=True)
    pd.DataFrame(rows).to_csv("results/noisy_qaoa.csv", index=False)
print("finished", flush=True)
