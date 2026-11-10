"""Post hoc (review Issue 2): what zero or few collisions can establish.

For each method/cell: crossing encounters, distinct crossing scenarios, collisions; exact one-sided
95% Clopper-Pearson upper bounds on the collision rate treating (a) encounters and (b) distinct
scenarios as the independent units (each scenario is replayed with the same tracker noise, and in
the pre-registered runs the same operator answers, whenever it is reused); and, for joint - rule,
one-sided 95% upper bounds of the difference from an epoch-cluster and a scenario-cluster bootstrap.
Writes results/posthoc/safety_stats.csv.
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = 10_000


def cp_upper(k, n, a=0.05):
    return 1.0 if k >= n else float(stats.beta.ppf(1 - a, k + 1, n - k))


def boot_diff(j, r, unit, rng):
    """j, r: crossing-robot rows (same encounters) with collision; unit: cluster column."""
    m = j[[unit, "collision"]].rename(columns={"collision": "cj"}).reset_index(drop=True)
    m["cr"] = r["collision"].to_numpy()
    g = m.groupby(unit).agg(cj=("cj", "sum"), cr=("cr", "sum"), n=("cj", "size"))
    idx = rng.integers(0, len(g), size=(B, len(g)))
    d = (g.cj.to_numpy()[idx].sum(1) - g.cr.to_numpy()[idx].sum(1)) / g.n.to_numpy()[idx].sum(1)
    return 100 * float(np.quantile(d, 0.95))


def summarise(d, pairs, label):
    rows, rng = [], np.random.default_rng(8_300_000)
    for keys, g in d.groupby(["N", "condition"]):
        for jm, rm in pairs:
            J = g[(g.method == jm) & (g.crossing == 1)].sort_values(["epoch", "robot"])
            R = g[(g.method == rm) & (g.crossing == 1)].sort_values(["epoch", "robot"])
            if J.empty or R.empty:
                continue
            assert (J.scenario.to_numpy() == R.scenario.to_numpy()).all()
            n, s = len(J), J.scenario.nunique()
            row = dict(source=label, N=keys[0], condition=keys[1], joint=jm, rule=rm, crossing_encounters=n,
                       distinct_crossing_scenarios=s, col_joint=int(J.collision.sum()), col_rule=int(R.collision.sum()),
                       scen_with_col_joint=J[J.collision == 1].scenario.nunique(),
                       scen_with_col_rule=R[R.collision == 1].scenario.nunique())
            for who, X, k in (("joint", J, row["col_joint"]), ("rule", R, row["col_rule"])):
                row[f"ub_enc_{who}_pct"] = 100 * cp_upper(k, n)
                row[f"ub_scen_{who}_pct"] = 100 * cp_upper(X[X.collision == 1].scenario.nunique(), s)
            row["diff_ub_epoch_pp"] = boot_diff(J, R, "epoch", rng)
            row["diff_ub_scenario_pp"] = boot_diff(J, R, "scenario", rng)
            rows.append(row)
    return rows


if __name__ == "__main__":
    out = []
    c = pd.read_csv(os.path.join(ROOT, "results", "final", "closed_loop_confirmatory.csv.gz"))
    c["condition"] = "noisy"
    out += summarise(c, [("joint", "rule_matched"), ("joint_a", "rule_a_matched")], "confirmatory (per-scenario answers)")
    e = pd.read_csv(os.path.join(ROOT, "results", "final", "closed_loop_exploratory.csv.gz"),
                    usecols=["N", "condition", "calibration", "epoch", "robot", "scenario", "method", "crossing", "collision"])
    e = e[(e.calibration == "isotonic_dw") & (e.condition == "nominal")]
    out += summarise(e, [("joint", "rule_matched"), ("joint_a", "rule_a_matched")], "exploratory nominal (per-scenario answers)")
    a = os.path.join(ROOT, "results", "posthoc", "alpha.csv.gz")
    if os.path.exists(a):
        out += summarise(pd.read_csv(a), [("joint_a_pq", "rule_a_pq"), ("joint_sym", "rule_sym_matched")] +
                         [(f"joint_sym_eps{x:g}", "rule_sym_matched") for x in (0.005, 0.01, 0.02)], "post hoc (per-question answers)")
    t = pd.DataFrame(out)
    os.makedirs(os.path.join(ROOT, "results", "posthoc"), exist_ok=True)
    t.to_csv(os.path.join(ROOT, "results", "posthoc", "safety_stats.csv"), index=False)
    pd.set_option("display.width", 250)
    print(t.round(3).to_string())
