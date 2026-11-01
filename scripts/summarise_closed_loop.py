"""Summarise results/closed_loop.csv into results/closed_loop_summary.md (exploratory)."""
import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

d = pd.read_csv("results/closed_loop.csv.gz")
d["collision"] = d.collision.astype(str).str.lower().eq("true").astype(int)
d["fallback"] = d.fallback.astype(str).str.lower().eq("true").astype(int)
E = d.epoch.nunique()
key = ["condition", "epoch", "robot"]


def wilson(k, n, z=1.96):
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return 100 * (c - h), 100 * (c + h)


def mcnemar(a, b):
    oa, ob = int(((a == 1) & (b == 0)).sum()), int(((a == 0) & (b == 1)).sum())
    return oa, ob, (binomtest(oa, oa + ob, 0.5).pvalue if oa + ob else 1.0)


L = ["# Closed-loop study, month 3 (exploratory, development seeds)", "",
     f"N = 6 robots per epoch, {E} paired epochs per cell, one operator answering serially "
     "(1.5 s per question), deadlines within a 1 s window. Cost model C = 100. "
     "Collisions are per crossing robot, with 95% Wilson intervals.", "",
     "| Condition | Calibration | Method | Collisions (%) | 95% CI | Questions / epoch | "
     "Unanswered (cautious fallback) / epoch | Mean delay (s) | Stopped with non-crosser (s) | "
     "Congestion (s / epoch) | Held for epoch (s) |",
     "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
order = {"raw": 0, "isotonic": 1, "isotonic_dw": 2}
for (cond, cal, m), g in sorted(d.groupby(["condition", "calibration", "method"]),
                                key=lambda x: (x[0][0], order[x[0][1]], x[0][2])):
    k, n = g[g.crossing == 1].collision.sum(), (g.crossing == 1).sum()
    lo, hi = wilson(k, n)
    cong = g.drop_duplicates("epoch").epoch_congestion_s.mean()
    L.append(f"| {cond} | {cal} | {m} | {100 * k / n:.1f} | [{lo:.1f}, {hi:.1f}] | "
             f"{g.n_asks.sum() / E:.2f} | {g.fallback.sum() / E:.2f} | {g.delay.mean():.2f} | "
             f"{g[g.crossing == 0].stopped_time.mean():.2f} | {cong:.2f} | {g.held_s.mean():.2f} |")

L += ["", "## Paired comparisons", "",
      "McNemar exact on collisions of crossing robots; Wilcoxon signed-rank on per-robot delay.", "",
      "| Comparison | Condition | Calibration | Only first collided | Only second collided | p (collisions) | "
      "Mean delay difference (s) | p (delay) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]


def get(cond, cal, m):
    return d[(d.condition == cond) & (d.calibration == cal) & (d.method == m)].sort_values(key)


for cond in ["nominal", "noisy"]:
    comps = [(f"independent vs joint_single", cal, ("independent", cal), ("joint_single", cal))
             for cal in ["raw", "isotonic", "isotonic_dw"]]
    comps += [(f"independent_costband vs joint_none", cal, ("independent_costband", cal), ("joint_none", cal))
              for cal in ["raw", "isotonic", "isotonic_dw"]]
    comps += [(f"independent_costband vs joint_queue", cal, ("independent_costband", cal), ("joint_queue", cal))
              for cal in ["raw", "isotonic", "isotonic_dw"]]
    comps += [(f"independent_costband vs joint_free (early commits)", cal, ("independent_costband", cal), ("joint_free", cal))
              for cal in ["isotonic", "isotonic_dw"]]
    comps += [(f"joint_free vs joint_queue (coordination)", cal, ("joint_free", cal), ("joint_queue", cal))
              for cal in ["isotonic", "isotonic_dw"]]
    comps += [("joint_none vs joint_single", "isotonic_dw", ("joint_none", "isotonic_dw"),
               ("joint_single", "isotonic_dw"))]
    comps += [(f"conventional vs decision-aware ({m})", "both", (m, "isotonic"), (m, "isotonic_dw"))
              for m in ["independent", "joint_single"]]
    for label, cal, (ma, ca), (mb, cb) in comps:
        A, B = get(cond, ca, ma), get(cond, cb, mb)
        cr = A.crossing.to_numpy() == 1
        oa, ob, p = mcnemar(A.collision.to_numpy()[cr], B.collision.to_numpy()[cr])
        dd = A.delay.to_numpy() - B.delay.to_numpy()
        pw = wilcoxon(dd).pvalue if np.any(dd != 0) else 1.0
        L.append(f"| {label} | {cond} | {cal} | {oa} | {ob} | {p:.3g} | {dd.mean():+.2f} | {pw:.3g} |")

ac = d[d.method.isin(["joint_single", "joint_queue"])].groupby(["method", "condition", "calibration"]).action.value_counts(normalize=True)
L += ["", "## Joint actions at the deadline", "", "0 = go, 1 = stop, 2 = ask.", "",
      ac.unstack().round(3).to_markdown()]
fam = d[d.crossing == 1].groupby(["condition", "method", "family"]).collision.mean().unstack().mul(100)
L += ["", "## Collisions by scenario family (crossing robots, %, all calibrations pooled)", "",
      fam.round(1).to_markdown()]
open("results/closed_loop_summary.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
