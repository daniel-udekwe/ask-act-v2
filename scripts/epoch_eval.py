"""Epoch-level evaluation with real calibrated probabilities (development pool only).

For each epoch, N robots draw Ask or Act scenarios (same draw for every calibrator
and solver). Each solver picks actions from the calibrated probabilities; outcomes
are scored against ground-truth intent. This previews RQ1 (coordination) and RQ3
(calibration behind an optimizer); the full multi-robot closed loop is month 3.

Writes results/epoch_eval.csv (per robot), results/epoch_summary.md.
"""
import itertools
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import binomtest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fleet_qubo.pool import ScenarioPool, realized
from fleet_qubo.classical import exhaustive, independent_rule, greedy_budget
from fleet_qubo.instances import GO, STOP, ASK

EPOCHS = 500
CONDITIONS = ["nominal", "noisy"]
SIZES = [6, 8]
LAYOUTS = ["none", "single", "tjunction"]
SOLVERS = {"exact": lambda inst, s: exhaustive(inst)["actions"],
           "greedy": lambda inst, s: greedy_budget(inst)["actions"],
           "independent_rule": lambda inst, s: independent_rule(inst, seed=s)["actions"]}

pool = ScenarioPool("results/deadline_probs.csv")
rows = []
for cond, N, layout in itertools.product(CONDITIONS, SIZES, LAYOUTS):
    for e in range(EPOCHS):
        seed = 4000_000 + e                       # development epochs
        rng = np.random.default_rng([seed, N])
        scen = pool.draw(cond, N, rng)
        cross = pool.crossing(cond, scen)
        for cal in pool.calibrations:
            inst = pool.instance(cond, scen, cal, layout)
            for sname, solve in SOLVERS.items():
                acts = solve(inst, seed)
                for i in range(N):
                    rows.append(dict(condition=cond, N=N, layout=layout, epoch=e, robot=i,
                                     scenario=scen[i], calibration=cal, solver=sname,
                                     p=inst.p[i], crossing=cross[i], action=int(acts[i]),
                                     budget_binds=int(((inst.p > 0.2) & (inst.p < 0.8)).sum() > inst.B)))
    print(cond, N, layout, flush=True)

df = pd.DataFrame(rows)
df["collision"] = ((df.action == GO) & (df.crossing == 1)).astype(int)
df["question"] = (df.action == ASK).astype(int)
df["unnec_stop"] = ((df.action == STOP) & (df.crossing == 0)).astype(int)
df.to_csv("results/epoch_eval.csv.gz", index=False)


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def mcnemar(a, b):
    """Exact McNemar on paired binary outcomes; returns (only_a, only_b, p)."""
    only_a = int(((a == 1) & (b == 0)).sum())
    only_b = int(((a == 0) & (b == 1)).sum())
    n = only_a + only_b
    p = binomtest(only_a, n, 0.5).pvalue if n else 1.0
    return only_a, only_b, p


lines = ["# Epoch-level evaluation with real calibrated probabilities",
         "", f"Development pool only (scenario seeds 4000-4099, {EPOCHS} epochs per cell). "
         "Collisions are per crossing robot, with 95% Wilson intervals.", ""]

# --- deadline calibration of the pool itself --------------------------------
def ece(y, p, bins=15):
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    return sum((idx == b).mean() * abs(y[idx == b].mean() - p[idx == b].mean())
               for b in range(bins) if (idx == b).any())

lines += ["## Probabilities at the deadline", "",
          "ECE of the probability at the deadline (one value per scenario).", "",
          "| Condition | Calibration | Scenarios | ECE at deadline | Share in ask band |",
          "| --- | --- | --- | --- | --- |"]
for cond in CONDITIONS:
    sub = pool.p.loc[cond]
    y = pool.meta.loc[cond].loc[sub.index, "crossing"].to_numpy()
    for cal in pool.calibrations:
        p = sub[cal].to_numpy()
        lines.append(f"| {cond} | {cal} | {len(p)} | {ece(y, p):.3f} | {((p > 0.2) & (p < 0.8)).mean():.2f} |")

# --- outcomes ---------------------------------------------------------------
lines += ["", "## Outcomes by solver and calibration", "",
          "| Condition | N | Layout | Calibration | Solver | Collisions (%) | 95% CI | Questions / epoch | Unnecessary stops / epoch |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for (cond, N, layout, cal, sol), g in df.groupby(["condition", "N", "layout", "calibration", "solver"], sort=False):
    k, n = g.collision.sum(), g.crossing.sum()
    lo, hi = wilson(k, n)
    lines.append(f"| {cond} | {N} | {layout} | {cal} | {sol} | {100 * k / n:.1f} | "
                 f"[{100 * lo:.1f}, {100 * hi:.1f}] | {g.question.sum() / EPOCHS:.2f} | "
                 f"{g.unnec_stop.sum() / EPOCHS:.2f} |")

# --- paired comparisons -----------------------------------------------------
key = ["condition", "N", "layout", "epoch", "robot"]
lines += ["", "## Paired comparisons (exploratory, McNemar exact, crossing robots only)", "",
          "| Comparison | Condition | N | Layout | Only first collided | Only second collided | p |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
cr = df[df.crossing == 1]
for cond, N, layout in itertools.product(CONDITIONS, SIZES, LAYOUTS):
    c = cr[(cr.condition == cond) & (cr.N == N) & (cr.layout == layout)]
    get = lambda cal, sol: c[(c.calibration == cal) & (c.solver == sol)].sort_values(key).collision.to_numpy()
    for label, a, b in [("independent rule vs exact (decision-aware)",
                         get("isotonic_dw", "independent_rule"), get("isotonic_dw", "exact")),
                        ("conventional vs decision-aware (exact)",
                         get("isotonic", "exact"), get("isotonic_dw", "exact"))]:
        oa, ob, p = mcnemar(a, b)
        lines.append(f"| {label} | {cond} | {N} | {layout} | {oa} | {ob} | {p:.3g} |")

bind = df.drop_duplicates(["condition", "N", "layout", "epoch", "calibration"]).groupby(
    ["condition", "N", "calibration"]).budget_binds.mean()
lines += ["", "## How often the question budget binds", "",
          "Share of epochs where more robots are in the ask band than the budget allows.", "",
          bind.reset_index().round(3).to_markdown(index=False)]

open("results/epoch_summary.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
