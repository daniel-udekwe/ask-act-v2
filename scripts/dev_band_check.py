"""Development check (3 Nov 2026): collisions of the Ask or Act fixed band [0.2, 0.8] with corrected probabilities. N=6, 200 epochs."""
import sys, os
sys.path.insert(0, "/home/claude/fleet_qubo/scripts"); sys.path.insert(0, "/home/claude/fleet_qubo")
import pareto, pandas as pd
pareto.EPOCH_SEED = 4_950_000
pareto.band = lambda k: (0.2, 0.8)
pareto.methods = lambda: [("indep", 0.0, 0.0)]
rows = []
for cond in ("noisy", "nominal"):
    for cal in ("isotonic", "isotonic_dw"):
        rows += pareto.task((cond, cal, list(range(200)), 6, 1.0))
d = pd.DataFrame(rows)
g = d.groupby(["condition", "calibration"])
r = (pd.DataFrame({"robots": g.size(), "crossing": g.crossing.sum(),
                    "collisions": g.collision.sum(),
                    "col_pct_crossing": 100 * d[d.crossing == 1].groupby(["condition", "calibration"]).collision.mean(),
                    "q_per_epoch": g.n_asks.sum() / 200, "delay": g.delay.mean()}))
print(r.to_string()); print(d.fallback.mean())
