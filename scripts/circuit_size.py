"""Two-qubit gate counts and depth after transpiling QAOA circuits to a
hardware-like target (CZ/ECR-style basis on a heavy-hex coupling map).
Writes results/circuit_size.csv."""
import os
import sys

import numpy as np
import pandas as pd
from qiskit import transpile
from qiskit.transpiler import CouplingMap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fleet_qubo.instances import make_instance
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem, qiskit_circuit

cmap = CouplingMap.from_heavy_hex(5)          # 57 qubits, IBM-style connectivity
rows = []
for N, layout in [(4, "none"), (6, "none"), (6, "single"), (8, "single")]:
    inst = make_instance(N, 3000, layout)
    for enc in ["slack", "unbalanced"]:
        prob = QaoaProblem(build_qubo(inst, enc), inst)
        for p in (1, 2, 3):
            qc = qiskit_circuit(prob, np.full(2 * p, 0.3), measure=True)
            t = transpile(qc, coupling_map=cmap, basis_gates=["rz", "sx", "x", "cz"],
                          optimization_level=3, seed_transpiler=0)
            ops = t.count_ops()
            rows.append({"N": N, "layout": layout, "encoding": enc, "depth_p": p,
                         "qubits": prob.n, "zz_terms": len(prob.qubo.quad),
                         "two_qubit_gates": ops.get("cz", 0), "circuit_depth": t.depth()})
            print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv("results/circuit_size.csv", index=False)
