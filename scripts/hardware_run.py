"""Pre-registered QAOA runs on IBM hardware (or a dry run on its noise model).

Everything that defines the run is read from prereg/hardware.json, frozen before the
final evaluation: sizes, instance seeds, QAOA variant, depths, shots, transpiler
settings and backend. The script refuses to run on hardware unless

  * the final scenario pool exists (results/final/deadline_probs.csv, seeds 8000-8099,
    made with extract_deadline_probs.py after the freeze), and
  * --confirm-frozen is passed.

Parameters are trained noiselessly in simulation, exactly as in the development runs;
only the sampling happens on hardware. All circuits go in one Batch.

Dry run (no account needed, development pool, FakeKingston noise model):
  python scripts/hardware_run.py --dry-run
Hardware (after the freeze; needs a saved IBM Quantum account, e.g.
QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token=..., instance=...)):
  python scripts/hardware_run.py --confirm-frozen
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
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from fleet_qubo.pool import ScenarioPool  # noqa: E402
from fleet_qubo.qubo import build_qubo  # noqa: E402
from fleet_qubo.instances import true_cost  # noqa: E402
from fleet_qubo.qaoa import QaoaProblem, optimise, interp, qiskit_circuit, warm_from_bits, evaluate  # noqa: E402


def counts_metrics(counts, prob):
    keys = np.array([int(k.replace(" ", ""), 2) for k in counts])
    w = np.array(list(counts.values()), dtype=float)
    w /= w.sum()
    feas = prob.state_feas[keys]
    cost = prob.state_cost[keys]
    best = cost[feas].min() if feas.any() else np.inf
    exp_cost = float(w[feas] @ cost[feas]) / w[feas].sum() if feas.any() else np.inf
    return dict(p_opt=float(w[prob.state_opt[keys]].sum()), p_feasible=float(w[feas].sum()),
                best_sample_gap=float((best - prob.opt_cost) / abs(prob.opt_cost)),
                feasible_cost_gap=float((exp_cost - prob.opt_cost) / abs(prob.opt_cost)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prereg", default=os.path.join(ROOT, "prereg", "hardware.json"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm-frozen", action="store_true")
    a = ap.parse_args()
    P = json.load(open(a.prereg))

    if a.dry_run:
        pool_path, out = os.path.join(ROOT, "results", "deadline_probs.csv"), "results/hardware_dryrun.csv"
        seed_base = P["dry_run_epoch_seed"]
        from qiskit_aer import AerSimulator
        from qiskit_ibm_runtime.fake_provider import FakeKingston
        backend = FakeKingston()
        runner = AerSimulator.from_backend(backend)
    else:
        pool_path, out = os.path.join(ROOT, "results", "final", "deadline_probs.csv"), "results/final/hardware.csv"
        seed_base = P["final_epoch_seed"]
        if not (a.confirm_frozen and os.path.exists(pool_path)):
            sys.exit("Refusing: pass --confirm-frozen after the freeze, and create the final pool first.")
        from qiskit_ibm_runtime import QiskitRuntimeService
        backend = QiskitRuntimeService().backend(P["backend"])

    from qiskit import transpile
    pool = ScenarioPool(pool_path)
    C = P["cost"]
    jobs, meta = [], []
    for N in P["sizes"]:
        for k in range(P["instances_per_size"]):
            scen = pool.draw(P["condition"], N, np.random.default_rng([seed_base + k, N]))
            inst = pool.instance(P["condition"], scen, P["calibration"], B=N, **C)
            inst.q = P["queue_cost"]
            prob = QaoaProblem(build_qubo(inst, "slack"), inst)
            acts = inst.unary_costs().argmin(axis=1)
            warm = None
            if P["variant"] == "warm":
                bits = np.concatenate([(acts == 2).astype(int), (acts == 1).astype(int)])
                warm = warm_from_bits(bits, P["warm_eps"])
            params = None
            for p in range(1, max(P["depths"]) + 1):
                params, _ = optimise(prob, p, init=interp(params) if params is not None else None,
                                     restarts=P["restarts"], seed=seed_base + k, warm=warm)
                if p not in P["depths"]:
                    continue
                qc = qiskit_circuit(prob, params, measure=True, warm=warm)
                best = None
                for s in range(P["transpile"]["seeds"]):
                    t = transpile(qc, backend, optimization_level=P["transpile"]["optimization_level"],
                                  seed_transpiler=s)
                    if best is None or t.count_ops().get("cz", 0) < best.count_ops().get("cz", 0):
                        best = t
                ideal = evaluate(params, prob, shots=P["shots"], seed=k, warm=warm)
                jobs.append(best)
                meta.append(dict(N=N, instance=k, depth=p, qubits=prob.n, cz_gates=best.count_ops().get("cz", 0),
                                 opt_cost=prob.opt_cost, heuristic_cost=true_cost(inst, acts),
                                 noiseless_p_opt=ideal["p_opt"], noiseless_p_feasible=ideal["p_feasible"],
                                 random_p_opt=ideal["random_p_opt"], prob=prob))
                print(f"prepared N={N} k={k} p={p} cz={meta[-1]['cz_gates']}", flush=True)

    t0 = time.time()
    if a.dry_run:
        results = [runner.run(c, shots=P["shots"], seed_simulator=i).result().get_counts()
                   for i, c in enumerate(jobs)]
    else:
        from qiskit_ibm_runtime import Batch, SamplerV2
        with Batch(backend=backend) as batch:
            sampler = SamplerV2(mode=batch)
            res = sampler.run(jobs, shots=P["shots"]).result()
        results = [r.data.meas.get_counts() for r in res]
    rows = []
    for m, counts in zip(meta, results):
        prob = m.pop("prob")
        rows.append({**m, **counts_metrics(counts, prob), "backend": P["backend"] if not a.dry_run else "FakeKingston"})
    os.makedirs(os.path.dirname(os.path.join(ROOT, out)), exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(ROOT, out), index=False)
    print(f"{len(rows)} circuits, {time.time() - t0:.0f} s; wrote {out}")


if __name__ == "__main__":
    main()
