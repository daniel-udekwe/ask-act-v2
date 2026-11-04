"""Pre-specified analysis of the final runs (ANALYSIS_PLAN.md sections 5-7).

Reads (whichever exist):
  results/final/closed_loop_confirmatory.csv.gz   -> H1a, H1b, H4a, H4b
  results/final/qaoa_h2.csv                        -> H2
  results/final/closed_loop_exploratory.csv.gz    -> section 7 tables
Writes results/final/REPORT.md (and results/final/confirmatory.csv, exploratory_summary.csv).

Usage: python scripts/fleet_final_stats.py [--dir results/final]
"""
import argparse
import os

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARGIN_PP = 0.5
BOOT = 10_000
BOOT_SEED = 8_300_000
HYP = [("H1a", 6, "joint", "rule_matched"), ("H1b", 8, "joint", "rule_matched"),
       ("H4a", 6, "joint_a", "rule_a_matched"), ("H4b", 8, "joint_a", "rule_a_matched")]


def per_epoch(d):
    """Epoch-level aggregates for one method: mean delay, crossing collisions, crossing robots, questions."""
    return d.groupby("epoch").agg(delay=("delay", "mean"), questions=("n_asks", "sum"),
                                  col=("collision", lambda x: int((x * d.loc[x.index, "crossing"]).sum())),
                                  cross=("crossing", "sum"))


def paired_test(d, N, jm, rm, rng):
    d = d[(d.N == N) & (d.condition == "noisy") & (d.calibration == "isotonic_dw")]
    J, R = per_epoch(d[d.method == jm]), per_epoch(d[d.method == rm])
    J, R = J.align(R, join="inner", axis=0)
    w = stats.wilcoxon(J.delay, R.delay, alternative="less", zero_method="wilcox")
    n_cross = R.cross.to_numpy()
    dc = (J.col - R.col).to_numpy()
    diff_pp = 100 * dc.sum() / n_cross.sum()
    idx = rng.integers(0, len(dc), size=(BOOT, len(dc)))
    boot = 100 * dc[idx].sum(axis=1) / n_cross[idx].sum(axis=1)
    ub = float(np.quantile(boot, 0.95))
    qj, qr = J.questions.mean(), R.questions.mean()
    return dict(N=N, joint=jm, rule=rm, epochs=len(J), crossing_robots=int(n_cross.sum()),
                delay_joint=J.delay.mean(), delay_rule=R.delay.mean(), delay_saved=(R.delay - J.delay).mean(),
                p_delay=float(w.pvalue), col_joint_pct=100 * J.col.sum() / n_cross.sum(),
                col_rule_pct=100 * R.col.sum() / n_cross.sum(), col_diff_pp=diff_pp, col_diff_ub95_pp=ub,
                noninferior=ub < MARGIN_PP, q_joint=qj, q_rule=qr, q_rel_diff=abs(qj - qr) / qj if qj else np.nan)


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, (len(p) - r) * p[i])
        adj[i] = min(1.0, run)
    return adj


def clopper_pearson(k, n, a=0.05):
    lo = stats.beta.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0
    hi = stats.beta.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0
    return lo, hi


def mcnemar(a, b):
    """Exact two-sided McNemar on paired binary outcomes."""
    n01, n10 = int(((a == 0) & (b == 1)).sum()), int(((a == 1) & (b == 0)).sum())
    p = stats.binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return n01, n10, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(ROOT, "results", "final"))
    a = ap.parse_args()
    out = ["# Final results (pre-specified analysis, ANALYSIS_PLAN.md)", ""]

    f = os.path.join(a.dir, "closed_loop_confirmatory.csv.gz")
    if os.path.exists(f):
        d = pd.read_csv(f)
        rng = np.random.default_rng(BOOT_SEED)
        t = pd.DataFrame([dict(hypothesis=h, **paired_test(d, N, jm, rm, rng)) for h, N, jm, rm in HYP])
        t["p_holm"] = holm(t.p_delay)
        t["supported"] = (t.p_holm < 0.05) & t.noninferior
        t["matching_deviation"] = t.q_rel_diff > 0.10
        t.to_csv(os.path.join(a.dir, "confirmatory.csv"), index=False)
        out += ["## Confirmatory: H1a, H1b, H4a, H4b", "",
                "Noisy tracking, decision-aware calibration. Delay: one-sided Wilcoxon on paired epoch means, "
                "Holm across the four. Collisions: crossing robots, joint − rule, one-sided 95% epoch-cluster "
                f"bootstrap bound ({BOOT:,} resamples), margin {MARGIN_PP} pp.", "",
                t[["hypothesis", "N", "joint", "rule", "epochs", "crossing_robots", "delay_joint", "delay_rule",
                   "delay_saved", "p_delay", "p_holm", "col_joint_pct", "col_rule_pct", "col_diff_ub95_pp",
                   "noninferior", "q_joint", "q_rule", "matching_deviation", "supported"]]
                .to_markdown(index=False, floatfmt=".4g"), ""]
        for r in t.itertuples():
            if r.matching_deviation:
                out.append(f"- Deviation: {r.hypothesis} questions per epoch differ by {100 * r.q_rel_diff:.1f}% "
                           f"(joint {r.q_joint:.3f}, rule {r.q_rule:.3f}); κ* not re-tuned.")
            if r.col_joint_pct == 0 and r.col_rule_pct == 0:
                out.append(f"- {r.hypothesis}: no collisions for either method; non-inferiority holds trivially.")
        out.append("")

    f = os.path.join(a.dir, "qaoa_h2.csv")
    if os.path.exists(f):
        q = pd.read_csv(f)
        rows = []
        for N, g in q.groupby("N"):
            k, n = int(g.h2_pass.sum()), len(g)
            lo, hi = clopper_pearson(k, n)
            rows.append(dict(N=N, instances=n, passed=k, share=k / n, ci_low=lo, ci_high=hi,
                             criterion_met=k / n >= 0.8, lift_median=g.lift.median(),
                             feasible_share_median=g.p_feasible.median(),
                             feasible_gap_median=g.feasible_cost_gap.median(),
                             random_gap_median=g.random_feasible_gap.median()))
        h2 = pd.DataFrame(rows)
        out += ["## H2: QAOA on the queue formulation (vanilla, depth 3, noiseless)", "",
                h2.to_markdown(index=False, floatfmt=".4g"), "",
                f"H2 {'MET' if h2.criterion_met.all() and set(h2.N) == {4, 6, 8} else 'NOT MET'} "
                "(share ≥ 80% at every N ∈ {4, 6, 8}).", ""]

    f = os.path.join(a.dir, "closed_loop_exploratory.csv.gz")
    if os.path.exists(f):
        d = pd.read_csv(f)
        keys = ["N", "condition", "calibration", "method"]
        nc = d[d.crossing == 0]
        s = d.groupby(keys + ["epoch"]).agg(q=("n_asks", "sum"), fb=("fallback", "sum")).groupby(keys).mean()
        s["collisions_pct"] = 100 * d[d.crossing == 1].groupby(keys).collision.mean()
        s["crossing_robots"] = d[d.crossing == 1].groupby(keys).size()
        s["delay_s"] = d.groupby(keys).delay.mean()
        s["stopped_noncrossing_s"] = nc.groupby(keys).stopped_time.mean()
        s["hold_s"] = d.groupby(keys).held_s.mean()
        s = s.rename(columns={"q": "questions_per_epoch", "fb": "unanswered_per_epoch"}).reset_index()
        s.to_csv(os.path.join(a.dir, "exploratory_summary.csv"), index=False)
        out += ["## Exploratory (section 7)", "",
                "Full table: `exploratory_summary.csv`. Noisy tracking, decision-aware calibration:", "",
                s[(s.condition == "noisy") & (s.calibration == "isotonic_dw")]
                .drop(columns=["condition", "calibration"]).to_markdown(index=False, floatfmt=".3f"), ""]
        out += ["### Calibration (formerly H3): decision-aware against conventional, N = 6, noisy", ""]
        for m in ("joint", "joint_a"):
            x = d[(d.N == 6) & (d.condition == "noisy") & (d.method == m) & (d.crossing == 1)]
            p = x.pivot_table(index=["epoch", "robot"], columns="calibration", values="collision")
            n01, n10, pv = mcnemar(p["isotonic"].to_numpy(), p["isotonic_dw"].to_numpy())
            out.append(f"- `{m}`: crossing robots {len(p)}; collisions decision-aware only {n01}, "
                       f"conventional only {n10}; exact McNemar p = {pv:.3g}")
        out.append("")
    open(os.path.join(a.dir, "REPORT.md"), "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
