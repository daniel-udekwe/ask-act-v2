"""Development check (3 Nov 2026): joint vs matched rule with 90% answer accuracy (solver still assumes alpha=1). N=6 noisy, 200 epochs."""
import sys, functools
sys.path.insert(0, "/home/claude/fleet_qubo/scripts"); sys.path.insert(0, "/home/claude/fleet_qubo")
import pareto, pandas as pd
from fleet_qubo import fleet_sim
pareto.EPOCH_SEED = 4_960_000
pareto.run_fleet = functools.partial(fleet_sim.run_fleet, answer_accuracy=0.9)
pareto.methods = lambda: [("indep", 5.95, 0.0), ("jq", 1.5, 1.5)]
rows = []
for cal in ("isotonic", "isotonic_dw"):
    rows += pareto.task(("noisy", cal, list(range(200)), 6, 1.0))
d = pd.DataFrame(rows)
c = d[d.crossing == 1]
print(pd.DataFrame({"collisions": c.groupby(["calibration", "kind"]).collision.sum(),
                    "crossing": c.groupby(["calibration", "kind"]).size(),
                    "q_per_epoch": d.groupby(["calibration", "kind"]).n_asks.sum() / 200,
                    "delay": d.groupby(["calibration", "kind"]).delay.mean()}).to_string())
