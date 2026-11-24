"""Probability-dependent action allocation (post hoc): paper/figures/allocation.pdf.

Input: results/posthoc/alloc.csv.gz (N = 6, noisy tracking, decision-aware calibration, 1,000 final
epochs, answers drawn per question). For each robot, p_dec is the calibrated probability at which the
method first acted on its pedestrian and act_dec that action (go / yield / ask); see
fleet_qubo.fleet_sim._decision_point. The deadline rule shown is the kappa whose question rate is
closest to the joint solver's.
"""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK, GRAY = "#2b2b29", "#8a8a85"
COL = {"go": "#1baf7a", "yield": "#eb6834", "ask": "#2a78d6"}
SCOL = {"joint": "#2a78d6", "deadline": "#6b6b66", "rule": "#eb6834"}
plt.rcParams.update({"font.family": "serif", "font.size": 7.5, "pdf.fonttype": 42})
BINS = np.round(np.arange(0.1, 1.0001, 0.1), 2)            # first bin [0.1, 0.2): no p below 0.13


def pick(d, alpha_tag):
    q = d.groupby(["method", "epoch"]).n_asks.sum().groupby("method").mean()
    jq = q[f"joint_{alpha_tag}"]
    dl = q[q.index.str.startswith(f"deadline_{alpha_tag}_")]
    return {"joint": f"joint_{alpha_tag}", "deadline": (dl - jq).abs().idxmin(), "rule": f"rule_{alpha_tag}"}, q


def main():
    d = pd.read_csv(os.path.join(ROOT, "results", "posthoc", "alloc.csv.gz"))
    d = d[d.act_dec.isin(["go", "yield", "ask"])].copy()
    d["bin"] = pd.cut(d.p_dec, BINS, right=False, labels=BINS[:-1])
    fig, axs = plt.subplots(2, 4, figsize=(7.4, 4.0), gridspec_kw=dict(width_ratios=[1, 1, 1, 1.15]))
    centers = BINS[:-1] + 0.05
    names = {"joint": "Joint solver", "deadline": "Per-robot rule at deadline", "rule": "Matched per-robot rule"}
    for r, (tag, alab) in enumerate((("a1", r"$\alpha = 1$"), ("a09", r"$\alpha = 0.9$"))):
        sel, q = pick(d, tag)
        for c, key in enumerate(("joint", "deadline", "rule")):
            ax = axs[r, c]; x = d[d.method == sel[key]]
            share = x.groupby("bin", observed=False).act_dec.value_counts(normalize=True).unstack(fill_value=0)
            share = share.reindex(BINS[:-1]).fillna(0)
            n = x.groupby("bin", observed=False).size().reindex(BINS[:-1]).fillna(0)
            bottom = np.zeros(len(share))
            for a in ("go", "yield", "ask"):
                v = share.get(a, pd.Series(0, index=share.index)).values
                ax.bar(centers, v, 0.092, bottom=bottom, color=COL[a], label=a.capitalize() if (r, c) == (0, 0) else None,
                       alpha=[1.0 if k >= 30 else 0.35 for k in n][0] if False else 1.0)
                bottom += v
            cr = x.groupby("bin", observed=False).crossing.mean().reindex(BINS[:-1])
            ax.plot(centers[n >= 30], cr[n >= 30], "o-", color=INK, ms=2.2, lw=0.8,
                    label="share crossing" if (r, c) == (0, 0) else None)
            ax.set_xlim(0.1, 1.0); ax.set_ylim(0, 1.0)
            ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
            if r == 1:
                ax.set_xlabel("calibrated probability $p_i$")
            if c == 0:
                ax.set_ylabel(f"{alab}\nshare of robots")
            else:
                ax.set_yticklabels([])
            qq = q[sel[key]]
            ax.set_title(f"{names[key]}\n{qq:.2f} questions/epoch" if r == 0 else f"{qq:.2f} questions/epoch",
                         fontsize=7.2, color=INK)
        # column 4
        ax = axs[r, 3]
        off = {"joint": -0.03, "deadline": 0.0, "rule": 0.03}
        if r == 0:
            for key in ("joint", "deadline", "rule"):
                x = d[(d.method == sel[key]) & (d.act_dec == "ask")]
                k = x.groupby("bin", observed=False).size().reindex(BINS[:-1]).fillna(0) / d.epoch.nunique()
                ax.bar(centers + off[key], k.values, 0.03, color=SCOL[key], label=names[key].replace("Per-robot rule at deadline", "Deadline rule").replace("Matched per-robot rule", "Matched rule"))
            ax.set_title("Questions by probability\n(per epoch)", fontsize=7.2, color=INK)
            ax.legend(fontsize=5.8, frameon=False, loc="upper right")
        else:
            for key in ("joint", "deadline", "rule"):
                x = d[(d.method == sel[key]) & (d.act_dec == "ask") & (d.crossing == 1)]
                w = x[x.answer == "not_crossing"]
                k = w.groupby("bin", observed=False).size().reindex(BINS[:-1]).fillna(0)
                cc = w[w.collision == 1].groupby("bin", observed=False).size().reindex(BINS[:-1]).fillna(0)
                ax.bar(centers + off[key], k.values, 0.03, color=SCOL[key])
                for xc, cv in zip(centers + off[key], cc.values):
                    if cv > 0:
                        ax.plot(xc, cv, "x", color=INK, ms=3.5, mew=1.0)
            ax.plot([], [], "x", color=INK, ms=3.5, label="ended in collision")
            ax.legend(fontsize=5.8, frameon=False, loc="upper right")
            ax.set_title("Wrong “not crossing” answers\nto crossing pedestrians (count)", fontsize=7.2, color=INK)
            ax.set_xlabel("calibrated probability $p_i$")
        ax.set_xlim(0.1, 1.0); ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9]); ax.grid(axis="y", alpha=0.25, lw=0.5)
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=7, frameon=False, bbox_to_anchor=(0.4, -0.01))
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=0.8, w_pad=0.5)
    fig.savefig(os.path.join(ROOT, "paper", "figures", "allocation.pdf")); plt.close(fig)
    for tag in ("a1", "a09"):
        sel, q = pick(d, tag); print(tag, sel, q[list(sel.values())].round(3).to_dict())


if __name__ == "__main__":
    main()
