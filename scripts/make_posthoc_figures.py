"""Post-hoc figures: safety comparison (collision rates with scenario-clustered 95% CIs) and the
operator-accuracy x cost-ratio sensitivity heatmap."""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(ROOT, "scripts", "make_paper_figures.py")).read().split("# Fig. 2")[0])
PH, FIN = os.path.join(ROOT, "results", "posthoc"), os.path.join(ROOT, "results", "final")
rng = np.random.default_rng(8_300_001)


def rate_ci(x):
    """Collision % on crossing robots with a 95% scenario-cluster bootstrap CI; zero events: CP bound on scenarios."""
    c = x[x.crossing == 1]
    k, n = c.collision.sum(), len(c)
    if k == 0:
        return 0.0, 0.0, 100 * stats.beta.ppf(0.95, 1, c.scenario.nunique())
    g = c.groupby("scenario").collision.agg(["sum", "size"])
    idx = rng.integers(0, len(g), size=(5000, len(g)))
    b = g["sum"].to_numpy()[idx].sum(1) / g["size"].to_numpy()[idx].sum(1)
    return 100 * k / n, 100 * np.quantile(b, 0.025), 100 * np.quantile(b, 0.975)


def safety():
    e = pd.read_csv(os.path.join(FIN, "closed_loop_exploratory.csv.gz"))
    e = e[(e.calibration == "isotonic_dw") & (e.N == 6)]
    a = pd.read_csv(os.path.join(PH, "alpha.csv.gz")); a = a[a.N == 6]
    groups = [("α = 1", e, "joint", "rule_matched"),
              ("α = 0.9\npre-registered", e, "joint_a", "rule_a_matched"),
              ("α = 0.9, per-question answers,\nsymmetric error cost", a, "joint_sym", "rule_sym_matched")]
    fig, axs = plt.subplots(3, 1, figsize=(7.2, 5.4), sharex=True)
    xt, GW = [], 2.7
    for gi, (name, d, jm, rm) in enumerate(groups):
        for ci, cond in enumerate(("nominal", "noisy")):
            x0 = gi * GW + ci * 1.05
            xt.append((x0, "nom." if cond == "nominal" else "noisy"))
            for k, (m, col, lab) in enumerate(((jm, BLUE, "joint solver"), (rm, ORANGE, "matched per-robot rule"))):
                x = d[(d.condition == cond) & (d.method == m)]
                r, lo, hi = rate_ci(x)
                xx = x0 + (k - 0.5) * 0.44
                if r > 0:
                    axs[0].bar(xx, r, 0.42, color=col, label=None)
                    axs[0].errorbar(xx, r, yerr=[[r - lo], [hi - r]], color=INK, lw=0.8, capsize=2)
                else:
                    axs[0].plot([xx, xx], [0, hi], color=col, lw=1.6, ls=(0, (2, 1.2)))
                    axs[0].plot(xx, 0, "o", ms=3.2, color=col, mec=col, label=lab if gi == 0 and ci == 0 and False else None)
                nc = x[x.crossing == 0]
                axs[1].bar(xx, nc.stopped_time.mean(), 0.42, color=col, label=lab if gi == 0 and ci == 0 else None)
                axs[2].bar(xx, x.groupby("epoch").n_asks.sum().mean(), 0.42, color=col)
    for ax, t, yl in zip(axs, ("(a) Collisions per crossing robot (95% CI, scenarios resampled)", "(b) Mean stopped time of robots whose pedestrian did not cross",
                               "(c) Questions per epoch"), ("%", "s", "questions")):
        ax.set_title(t, fontsize=8.2, color=INK, loc="left"); ax.set_ylabel(yl)
        ax.set_xlim(-0.6, 2 * GW + 1.65)
    axs[2].set_xticks([p for p, _ in xt], [l for _, l in xt], fontsize=7)
    for gi, (name, *_r) in enumerate(groups):
        axs[2].text(gi * GW + 0.525, -0.2, name, transform=axs[2].get_xaxis_transform(), ha="center", va="top", fontsize=7, color=INK)
    axs[0].axhline(0.5, color=GRAY, ls=":", lw=0.9)
    axs[0].text(2 * GW + 1.6, 0.53, "margin", fontsize=5.8, color=GRAY, ha="right", va="bottom")
    axs[0].plot([], [], color=INK, lw=1.4, ls=(0, (2, 1.2)), label="no collisions:\n95% upper bound")
    axs[0].legend(fontsize=6.5, loc="upper left", frameon=False)
    axs[1].legend(fontsize=6.5, loc="upper left", frameon=False)
    fig.tight_layout(rect=(0, 0.04, 1, 1), h_pad=0.6); fig.savefig(os.path.join(ROOT, "paper", "figures", "safety.pdf")); plt.close(fig)


def heatmap():
    d = pd.read_csv(os.path.join(PH, "grid.csv.gz"))
    d["ratio"] = d.C / 10.0
    A, Rt = sorted(d.alpha.unique()), sorted(d.ratio.unique())
    def grid(m, f):
        return np.array([[f(d[(d.method == m) & (d.alpha == a) & (d.ratio == r)]) for a in A] for r in Rt])
    col = lambda x: 100 * x[x.crossing == 1].collision.mean()
    J, Rr = grid("joint_sym", col), grid("rule_sym", col)
    qf = lambda x: x.groupby("epoch").n_asks.sum().mean()
    QJ, QR = grid("joint_sym", qf), grid("rule_sym", qf)
    fig, axs = plt.subplots(1, 4, figsize=(7.4, 2.35))
    cm, qm = max(J.max(), Rr.max()), max(QJ.max(), QR.max())
    for ax, M, t, cmap, vm, fmt in ((axs[0], J, "(a) Joint: collisions (%)", "Reds", cm, "{:.1f}"),
                                    (axs[1], Rr, "(b) Rule: collisions (%)", "Reds", cm, "{:.1f}"),
                                    (axs[2], QJ, "(c) Joint: questions/epoch", "Blues", qm, "{:.1f}"),
                                    (axs[3], QR, "(d) Rule: questions/epoch", "Blues", qm, "{:.1f}")):
        ax.imshow(M, origin="lower", cmap=cmap, vmin=0, vmax=vm, aspect="auto")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax.text(j, i, fmt.format(M[i, j]), ha="center", va="center", fontsize=5.6,
                        color="white" if M[i, j] > 0.6 * vm else INK)
        ax.set_xticks(range(len(A)), [f"{a:g}" for a in A], fontsize=6)
        ax.set_yticks(range(len(Rt)), [f"{r:g}" for r in Rt] if ax is axs[0] else [], fontsize=6.5)
        ax.set_xlabel("Answer accuracy α", fontsize=7); ax.set_title(t, fontsize=7.6, color=INK); ax.grid(False)
        ax.add_patch(plt.Rectangle((A.index(0.9) - 0.5, Rt.index(10.0) - 0.5), 1, 1, fill=False, ec=INK, lw=1.2))
    axs[0].set_ylabel(r"Cost ratio $C/\tau_s$", fontsize=7)
    fig.tight_layout(w_pad=0.6); fig.savefig(os.path.join(ROOT, "paper", "figures", "sensitivity.pdf")); plt.close(fig)


if __name__ == "__main__":
    if os.path.exists(os.path.join(PH, "alpha.csv.gz")):
        safety(); print("safety written")
    if os.path.exists(os.path.join(PH, "grid.csv.gz")):
        heatmap(); print("heatmap written")
