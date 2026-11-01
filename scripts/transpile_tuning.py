"""Month 5: how few CZ gates can a queue-formulation QAOA circuit use on ibm_kingston?

Strategies (FakeKingston target, Heron r2):
  level1         optimization_level=1, seed 0
  level3         optimization_level=3, seed 0 (used in months 2-4)
  level3_best20  optimization_level=3, best of 20 transpiler seeds
  swap_line      Qiskit's commuting-gate router with a line swap strategy (the
                 "QAOA with swap strategies" approach), placed on a line of physical
                 qubits, then optimization_level=3

Writes results/transpile_tuning.csv.
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import rustworkx as rx
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes.routing.commuting_2q_gate_routing import (
    SwapStrategy, FindCommutingPauliEvolutions, Commuting2qGateRouter)
from qiskit_ibm_runtime.fake_provider import FakeKingston

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from fleet_qubo.pool import ScenarioPool  # noqa: E402
from fleet_qubo.qubo import build_qubo  # noqa: E402
from fleet_qubo.qaoa import QaoaProblem, qiskit_circuit, qiskit_cost_operator  # noqa: E402
from qaoa_variants import instance  # noqa: E402

backend = FakeKingston()


def split_operator(op: SparsePauliOp):
    zz, z = [], []
    for pauli, coef in zip(op.paulis, op.coeffs):
        w = sum(1 for ch in pauli.to_label() if ch != "I")
        if w == 2:
            zz.append((pauli, coef))
        elif w == 1:
            z.append((pauli, coef))
    mk = lambda t: SparsePauliOp([p for p, _ in t], [c for _, c in t]) if t else None
    return mk(zz), mk(z)


def line_qaoa(prob, params):
    """Standard QAOA built from ZZ and Z evolutions, routed with a line swap strategy."""
    n, p = prob.n, len(params) // 2
    zz, z = split_operator(qiskit_cost_operator(prob))
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for g, b in zip(params[:p], params[p:]):
        qc.append(PauliEvolutionGate(zz, time=g), range(n))
        if z is not None:
            qc.append(PauliEvolutionGate(z, time=g), range(n))
        qc.rx(2 * b, range(n))
    strat = SwapStrategy.from_line(list(range(n)))
    colour = {e: (min(e) + 1) % 2 for i in range(n - 1) for e in ((i, i + 1), (i + 1, i))}
    routed = PassManager([FindCommutingPauliEvolutions(), Commuting2qGateRouter(strat)]).run(qc)
    routed.measure_all()
    return routed


def best_line(n):
    """A path of n physical qubits with the lowest summed CZ error."""
    target = backend.target
    g = rx.PyGraph()
    g.add_nodes_from(range(backend.num_qubits))
    err = {}
    for (a, b), props in target["cz"].items():
        e = props.error if props is not None and props.error is not None else 1e-2
        err[(min(a, b), max(a, b))] = e
    for (a, b), e in err.items():
        g.add_edge(a, b, e)
    best, best_e = None, np.inf
    for start in range(backend.num_qubits):           # greedy walk from every start
        path, used = [start], {start}
        while len(path) < n:
            nbrs = [(err[(min(path[-1], v), max(path[-1], v))], v) for v in g.neighbors(path[-1]) if v not in used]
            if not nbrs:
                break
            e, v = min(nbrs)
            path.append(v)
            used.add(v)
        if len(path) == n:
            tot = sum(err[(min(u, v), max(u, v))] for u, v in zip(path, path[1:]))
            if tot < best_e:
                best, best_e = path, tot
    return best


pool = ScenarioPool(os.path.join(ROOT, "results", "deadline_probs.csv"))
rows = []
for N in (4, 6, 8):
    inst = instance(pool, N, 0)
    prob = QaoaProblem(build_qubo(inst, "slack"), inst)
    for depth in (1, 2):
        params = np.full(2 * depth, 0.3)
        qc = qiskit_circuit(prob, params, measure=True)
        cands = {}
        t0 = time.time(); cands["level1"] = transpile(qc, backend, optimization_level=1, seed_transpiler=0); t1 = time.time() - t0
        t0 = time.time(); cands["level3"] = transpile(qc, backend, optimization_level=3, seed_transpiler=0); t3 = time.time() - t0
        best = None
        t0 = time.time()
        for s in range(20):
            t = transpile(qc, backend, optimization_level=3, seed_transpiler=s)
            if best is None or t.count_ops().get("cz", 0) < best.count_ops().get("cz", 0):
                best = t
        cands["level3_best20"] = best; tb = time.time() - t0
        t0 = time.time()
        lq = line_qaoa(prob, params)
        cands["swap_line"] = transpile(lq, backend, optimization_level=3, initial_layout=best_line(prob.n),
                                       seed_transpiler=0)
        ts = time.time() - t0
        for name, t in cands.items():
            ops = t.count_ops()
            rows.append(dict(N=N, qubits=prob.n, depth=depth, strategy=name, cz=ops.get("cz", 0),
                             circuit_depth=t.depth(), cz_layers=t.depth(lambda x: x.operation.name == "cz"),
                             secs=round({"level1": t1, "level3": t3, "level3_best20": tb, "swap_line": ts}[name], 1)))
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "transpile_tuning.csv"), index=False)
print("finished")
