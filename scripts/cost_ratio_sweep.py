"""Sensitivity of epoch outcomes to the collision cost C (development pool only).

tau_s = 10 and tau_a + kappa = 2 are fixed; C is swept. With C = 10 the uncoupled
optimum is the symmetric Ask or Act band, which implies a collision costs the same
as an unnecessary stop. Writes results/cost_ratio_sweep.csv and .md.
"""
import itertools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fleet_qubo.pool import ScenarioPool
from fleet_qubo.classical import exhaustive, independent_rule
from fleet_qubo.instances import GO, STOP, ASK

EPOCHS = 500
pool = ScenarioPool("results/deadline_probs.csv")
rows = []
for cond, layout, C, cal in itertools.product(["nominal", "noisy"], ["none", "single"],
                                               [10, 25, 50, 100], pool.calibrations):
    agg = {"exact": np.zeros(4), "independent_rule": np.zeros(4)}
    for e in range(EPOCHS):
        seed = 4000_000 + e
        rng = np.random.default_rng([seed, 6])
        scen = pool.draw(cond, 6, rng)
        cross = pool.crossing(cond, scen).astype(bool)
        inst = pool.instance(cond, scen, cal, layout, C=float(C))
        for name, acts in (("exact", exhaustive(inst)["actions"]),
                           ("independent_rule", independent_rule(inst, seed=seed)["actions"])):
            agg[name] += [((acts == GO) & cross).sum(), cross.sum(),
                          (acts == ASK).sum(), ((acts == STOP) & ~cross).sum()]
    for name, (col, ncr, q, us) in agg.items():
        rows.append(dict(condition=cond, layout=layout, C=C, calibration=cal, solver=name,
                         collisions_pct=100 * col / ncr, questions=q / EPOCHS,
                         unnecessary_stops=us / EPOCHS, go_threshold_if_no_question=round(10 / (C + 10), 3)))
    print(cond, layout, C, cal, flush=True)

df = pd.DataFrame(rows)
df.to_csv("results/cost_ratio_sweep.csv", index=False)
tab = df.pivot_table(index=["condition", "layout", "calibration", "C"], columns="solver",
                     values=["collisions_pct", "unnecessary_stops"]).round(2)
open("results/cost_ratio_sweep.md", "w").write(
    "# Collision-cost sweep (N = 6, development pool, 500 epochs per cell)\n\n"
    "A robot that cannot ask goes when p < 10 / (C + 10).\n\n" + tab.to_markdown() + "\n")
print(tab.to_string())
