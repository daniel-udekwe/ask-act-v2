"""Fix the H1 comparator on development data: the per-robot rule whose question rate matches
the primary joint solver (kappa = 1.5, q = 1.5), for N = 6 and 8, noisy tracking,
decision-aware calibration. The matched kappa is frozen in ANALYSIS_PLAN.md.

Writes results/dev_matching.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pareto  # noqa: E402

pareto.EPOCH_SEED = 4_900_000                     # fresh development epoch block
GRID = [3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.25, 5.5]
pareto.methods = lambda: [("indep", k, 0.0) for k in GRID] + [("jq", 1.5, 1.5)]

if __name__ == "__main__":
    from multiprocessing import Pool
    jobs = [("noisy", "isotonic_dw", list(e), N, 1.0) for N in (6, 8) for e in np.array_split(np.arange(500), 4)]
    with Pool(2) as p:
        rows = [r for chunk in p.map(pareto.task, jobs) for r in chunk]
    d = pd.DataFrame(rows)
    s = d.groupby(["N", "kind", "kappa"]).apply(lambda x: pd.Series({
        "questions": x.groupby("epoch").n_asks.sum().mean(),
        "collisions_pct": 100 * x[x.crossing == 1].collision.mean(),
        "delay_s": x.delay.mean()})).reset_index()
    s.to_csv(os.path.join(pareto.ROOT, "results", "dev_matching.csv"), index=False)
    print(s.round(3).to_string())
    for N in (6, 8):
        j = s[(s.N == N) & (s.kind == "jq")].iloc[0]
        ind = s[(s.N == N) & (s.kind == "indep")].sort_values("questions")
        k = float(np.interp(j.questions, ind.questions, ind.kappa))
        print(f"N = {N}: joint asks {j.questions:.3f} per epoch; matched per-robot kappa = {k:.3f}")
