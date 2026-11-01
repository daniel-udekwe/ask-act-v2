"""Summarise results/pareto.csv: frontier table, matched-rate comparisons, figure."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import binomtest

d = pd.read_csv("results/pareto.csv.gz")
E = d.groupby(["N", "condition", "calibration"]).epoch.nunique().min()


def label(r):
    return f"indep κ={r.kappa:g}" if r.kind == "indep" else f"joint κ={r.kappa:g} q={r.q:g}"


d["method"] = d.apply(label, axis=1)
d["family"] = np.where(d.kind == "indep", "Per-robot rule (κ swept)",
                       np.where(d.q == 1.5, "Joint, queue q = 1.5 (κ swept)", "Joint, κ = 0.5 (q swept)"))
g = d.groupby(["N", "condition", "calibration", "family", "kind", "kappa", "q", "method"])
s = g.apply(lambda x: pd.Series({
    "questions": x.groupby("epoch").n_asks.sum().mean(),
    "collisions_pct": 100 * x[x.crossing == 1].collision.mean(),
    "n_crossing": int((x.crossing == 1).sum()),
    "delay_s": x.delay.mean(),
    "fallbacks": x.groupby("epoch").fallback.sum().mean()})).reset_index()
s.to_csv("results/pareto_summary.csv", index=False)

# ---- matched-rate comparison: each joint point vs the per-robot point with the nearest question rate
key = ["epoch", "robot"]
rows = []
for (N, cond, cal), sub in d.groupby(["N", "condition", "calibration"]):
    ss = s[(s.N == N) & (s.condition == cond) & (s.calibration == cal)]
    ind = ss[ss.kind == "indep"]
    for r in ss[ss.kind == "jq"].itertuples():
        m = ind.iloc[(ind.questions - r.questions).abs().argmin()]
        A = sub[sub.method == r.method].sort_values(key)
        B = sub[sub.method == m.method].sort_values(key)
        cr = A.crossing.to_numpy() == 1
        a, b = A.collision.to_numpy()[cr], B.collision.to_numpy()[cr]
        ja, jb = int(((a == 1) & (b == 0)).sum()), int(((a == 0) & (b == 1)).sum())
        p = binomtest(ja, ja + jb, 0.5).pvalue if ja + jb else 1.0
        rows.append(dict(N=N, condition=cond, calibration=cal, joint=r.method, joint_questions=r.questions,
                         matched_rule=m.method, rule_questions=m.questions,
                         joint_collisions_pct=r.collisions_pct, rule_collisions_pct=m.collisions_pct,
                         only_joint_collided=ja, only_rule_collided=jb, p=p,
                         joint_delay=r.delay_s, rule_delay=m.delay_s))
mt = pd.DataFrame(rows)
mt.to_csv("results/pareto_matched.csv", index=False)

# ---- figure: questions vs collisions (top) and vs delay (bottom), decision-aware, noisy + nominal
COL = {"Per-robot rule (κ swept)": ("#2a78d6", "o"), "Joint, queue q = 1.5 (κ swept)": ("#eb6834", "s"),
       "Joint, κ = 0.5 (q swept)": ("#1baf7a", "^")}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlecolor": INK})
for cal in ["isotonic_dw", "isotonic"]:
    fig, axes = plt.subplots(2, 4, figsize=(13, 6.4), sharex="col")
    for j, (cond, N) in enumerate([("noisy", 6), ("noisy", 8), ("nominal", 6), ("nominal", 8)]):
        ss = s[(s.N == N) & (s.condition == cond) & (s.calibration == cal)]
        for i, metric in enumerate(["collisions_pct", "delay_s"]):
            ax = axes[i, j]
            for fam, (c, mk) in COL.items():
                f = ss[ss.family == fam].sort_values("questions")
                ax.plot(f.questions, f[metric], color=c, lw=2, marker=mk, ms=6,
                        markeredgecolor="white", markeredgewidth=1, label=fam)
            ax.grid(color=GRID, lw=0.6)
            ax.set_axisbelow(True)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            if i == 0:
                ax.set_title(f"{cond} tracking, N = {N}", fontsize=10)
                ax.set_ylim(bottom=0)
            if i == 1:
                ax.set_xlabel("Questions per epoch")
        axes[0, 0].set_ylabel("Collisions on crossing robots (%)")
        axes[1, 0].set_ylabel("Mean delay per robot (s)")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.955))
    name = "decision-aware" if cal == "isotonic_dw" else "conventional"
    fig.suptitle(f"At the same question rate the joint solver saves delay, not collisions "
                 f"({name} calibration, {E} epochs per point)", y=0.995, fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(f"results/pareto_{name}.png", dpi=150, bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)

# ---- markdown
L = ["# Pareto study: operator load against safety and delay (month 4, development seeds)", "",
     f"{E} paired epochs per point. Collisions are per crossing robot. Ask cost = 1.5 + κ.", "",
     "## Frontier", "", s.drop(columns=["family", "kind"]).round(3).to_markdown(index=False), "",
     "## Matched question rate", "",
     "Each joint point against the per-robot rule with the nearest question rate (McNemar exact on "
     "crossing robots, development seeds, exploratory).", "", mt.round(3).to_markdown(index=False)]
open("results/pareto_summary.md", "w").write("\n".join(L) + "\n")
print(mt[mt.condition == "noisy"].round(2).to_string())

# ---- interpolated comparison: per-robot curve evaluated at each joint point's question rate
irows = []
for (N, cond, cal), ss in s.groupby(["N", "condition", "calibration"]):
    ind = ss[ss.kind == "indep"].sort_values("questions")
    for r in ss[(ss.kind == "jq")].itertuples():
        if not ind.questions.min() <= r.questions <= ind.questions.max():
            continue
        irows.append(dict(N=N, condition=cond, calibration=cal, joint=r.method, questions=r.questions,
                          joint_delay=r.delay_s, rule_delay_interp=np.interp(r.questions, ind.questions, ind.delay_s),
                          joint_col=r.collisions_pct,
                          rule_col_interp=np.interp(r.questions, ind.questions, ind.collisions_pct)))
it = pd.DataFrame(irows)
it["delay_saved_s"] = it.rule_delay_interp - it.joint_delay
it["col_diff_pp"] = it.joint_col - it.rule_col_interp
it.to_csv("results/pareto_interp.csv", index=False)
agg = it.groupby(["N", "condition", "calibration"]).agg(
    points=("joint", "size"), delay_saved_mean=("delay_saved_s", "mean"),
    delay_saved_min=("delay_saved_s", "min"), delay_saved_max=("delay_saved_s", "max"),
    col_diff_mean_pp=("col_diff_pp", "mean"), col_diff_max_pp=("col_diff_pp", "max")).round(3)
with open("results/pareto_summary.md", "a") as f:
    f.write("\n## Joint against the per-robot frontier, interpolated at the same question rate\n\n"
            "Delay saved = per-robot delay minus joint delay (s per robot); collision difference = joint "
            "minus per-robot (percentage points).\n\n" + agg.to_markdown() + "\n")
print(agg.to_string())
