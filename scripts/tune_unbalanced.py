"""Tune unbalanced-penalization weights (lam_1, lam_2) on tuning seeds 1000-1049.

Criterion: share of instances whose QUBO ground state decodes to a true optimum.
Ties are broken toward smaller weights (a flatter landscape for QAOA).
Writes results/tune_unbalanced.csv and results/up_weights.json.
"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fleet_qubo.instances import make_instance
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem

SEEDS = range(1000, 1050)
SIZES = [4, 6]
LAYOUTS = ["none", "single"]
L1 = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
L2 = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

rows = []
for l1, l2 in itertools.product(L1, L2):
    ok = []
    for N, layout, seed in itertools.product(SIZES, LAYOUTS, SEEDS):
        inst = make_instance(N, seed, layout)
        prob = QaoaProblem(build_qubo(inst, "unbalanced", {"lam_1": l1, "lam_2": l2}), inst)
        ok.append(prob.ground_state_ok)
    rows.append({"lam_1": l1, "lam_2": l2, "ground_state_ok": float(np.mean(ok))})
    print(rows[-1], flush=True)

df = pd.DataFrame(rows)
os.makedirs("results", exist_ok=True)
df.to_csv("results/tune_unbalanced.csv", index=False)
best = df.sort_values(["ground_state_ok", "lam_2", "lam_1"], ascending=[False, True, True]).iloc[0]
json.dump({"lam_1": float(best.lam_1), "lam_2": float(best.lam_2),
           "ground_state_ok": float(best.ground_state_ok)}, open("results/up_weights.json", "w"), indent=2)
print("chosen", best.to_dict())
