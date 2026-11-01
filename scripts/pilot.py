"""Month-1 pilot: noiseless QAOA vs classical baselines on development seeds 3000-3009.

Stage 1 (budget only, layout "none") is the main pilot; a small stage-2 preview
(corridor layouts) is included and labelled exploratory. Writes results/pilot.csv.
"""
import itertools
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fleet_qubo.instances import make_instance
from fleet_qubo.qubo import build_qubo
from fleet_qubo.classical import exhaustive, cpsat, simulated_annealing, greedy_budget, independent_rule
from fleet_qubo.qaoa import run_qaoa

SEEDS = range(3000, 3010)
CONFIGS = [(4, "none"), (6, "none"), (6, "single"), (6, "tjunction")]
UP = json.load(open("results/up_weights.json"))
VARIANTS = [("slack", None), ("slack", 0.1), ("unbalanced", None), ("unbalanced", 0.1)]
DEPTHS = (1, 2, 3)

rows, out = [], "results/pilot.csv"
for (N, layout), seed in itertools.product(CONFIGS, SEEDS):
    inst = make_instance(N, seed, layout)
    ex = exhaustive(inst)
    opt = ex["cost"]
    base = {"N": N, "layout": layout, "seed": seed, "B": inst.B, "opt_cost": opt,
            "n_ambiguous": int(((inst.p > 0.2) & (inst.p < 0.8)).sum())}
    gap = lambda c: (c - opt) / abs(opt)
    cp = cpsat(inst)
    sa = simulated_annealing(build_qubo(inst, "slack"), inst, seed=seed)
    classical = {
        "cpsat": (gap(cp["cost"]), cp["time"]),
        "sim_annealing": (gap(sa["cost"]), sa["time"]),
        "greedy": (gap(greedy_budget(inst)["cost"]), 0.0),
        "independent_rule": (gap(independent_rule(inst, seed=seed)["cost"]), 0.0),
    }
    for name, (g, t) in classical.items():
        rows.append({**base, "solver": name, "depth": None, "best_sample_gap": g,
                     "found_opt": g <= 1e-9, "within_5pct": g <= 0.05, "time": t})
    for enc, cvar in VARIANTS:
        pen = {"lam_1": UP["lam_1"], "lam_2": UP["lam_2"]} if enc == "unbalanced" else None
        q = build_qubo(inst, enc, pen)
        for r in run_qaoa(q, inst, depths=DEPTHS, cvar=cvar, seed=seed):
            r.pop("params")
            rows.append({**base, "solver": f"qaoa_{enc}" + ("_cvar" if cvar else ""), **r})
    pd.DataFrame(rows).to_csv(out, index=False)
    print(time.strftime("%H:%M:%S"), N, layout, seed, "done", flush=True)
print("finished", flush=True)
