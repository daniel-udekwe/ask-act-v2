"""Figures for the paper, from the final results only (results/final/)."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R, OUT = os.path.join(ROOT, "results", "final"), os.path.join(ROOT, "paper", "figures")
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8a85", "#2b2b29"
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.edgecolor": GRAY, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e3", "grid.linewidth": 0.6, "legend.frameon": False,
                     "lines.linewidth": 1.6, "pdf.fonttype": 42})

# Fig. 2: operator load against delay
s = pd.read_csv(os.path.join(R, "exploratory_summary.csv"))
s = s[(s.condition == "noisy") & (s.calibration == "isotonic_dw")]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), sharey=True)
for ax, N in zip(axes, (6, 8)):
    x = s[s.N == N]
    r = x[x.method.str.match(r"rule_k[\d.]+$")].copy(); r["k"] = r.method.str[6:].astype(float); r = r.sort_values("k")
    j = x[x.method.str.match(r"joint_k[\d.]+$") | (x.method == "joint")].copy()
    j["k"] = j.method.map(lambda m: 1.5 if m == "joint" else float(m[7:])); j = j.sort_values("k")
    ax.plot(r.questions_per_epoch, r.delay_s, "-o", color=ORANGE, ms=4, label="Per-robot rule (κ swept)")
    ax.plot(j.questions_per_epoch, j.delay_s, "-s", color=BLUE, ms=4, label="Joint solver (κ swept)")
    b = x[x.method == "aoa_band"].iloc[0]
    ax.plot(b.questions_per_epoch, b.delay_s, "D", color=AQUA, ms=6, mec="white", mew=1, label="Ask or Act band [0.2, 0.8]")
    jm, rm = x[x.method == "joint"].iloc[0], x[x.method == "rule_matched"].iloc[0]
    ax.annotate("", xy=(jm.questions_per_epoch, jm.delay_s), xytext=(rm.questions_per_epoch, rm.delay_s),
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
    ax.plot(rm.questions_per_epoch, rm.delay_s, "o", ms=8, mfc="none", mec=INK, mew=0.9)
    ax.plot(jm.questions_per_epoch, jm.delay_s, "s", ms=8, mfc="none", mec=INK, mew=0.9)
    ax.text(rm.questions_per_epoch + 0.25, rm.delay_s + 0.05, "matched rule", color=INK, fontsize=7)
    ax.text(jm.questions_per_epoch + 0.25, jm.delay_s - 0.35, "joint (κ = 1.5)", color=INK, fontsize=7)
    ax.set_title(f"N = {N}", color=INK, fontsize=8.5)
    ax.set_xlabel("Questions per decision epoch")
axes[0].set_ylabel("Mean delay per robot (s)")
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, loc="lower center", ncol=3, fontsize=7.5, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(os.path.join(OUT, "pareto.pdf")); plt.close(fig)

# Fig. 3: QAOA lift, noiseless benchmark and hardware
q = pd.read_csv(os.path.join(R, "qaoa_h2.csv"))
h = pd.read_csv(os.path.join(R, "hardware.csv"))
h["lift_hw"], h["lift_sim"] = h.p_opt / h.random_p_opt, h.noiseless_p_opt / h.random_p_opt
fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.6))
rng = np.random.default_rng(0)
for i, N in enumerate((4, 6, 8)):
    v = q[q.N == N].lift
    a.plot(i + rng.uniform(-0.12, 0.12, len(v)), v, "o", color=BLUE, ms=3.5, alpha=0.8)
    a.plot([i - 0.25, i + 0.25], [v.median()] * 2, color=INK, lw=1.2)
a.axhline(10, color=GRAY, ls="--", lw=0.9); a.text(2.35, 11, "H2 threshold (10×)", color=INK, fontsize=7, ha="right")
a.set_yscale("log"); a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}")); a.set_xticks([0, 1, 2], ["N = 4\n(8 qubits)", "N = 6\n(12)", "N = 8\n(16)"])
a.set_ylabel("Lift over uniform sampling"); a.set_title("(a) Noiseless, depth 3, 20 instances per N", fontsize=8.5, color=INK)
labels = []
for i, ((N, p), g) in enumerate(h.groupby(["N", "depth"])):
    a2 = g.lift_sim.to_numpy(); b2 = g.lift_hw.to_numpy()
    b.plot(i - 0.14 + rng.uniform(-0.05, 0.05, len(a2)), a2, "o", color=GRAY, ms=3.5, alpha=0.8, label="Noiseless" if i == 0 else None)
    b.plot(i + 0.14 + rng.uniform(-0.05, 0.05, len(b2)), b2, "s", color=ORANGE, ms=3.5, alpha=0.85, label="ibm_kingston" if i == 0 else None)
    labels.append(f"N={N}, p={p}\n{int(g.cz_gates.iloc[0])} CZ")
b.set_yscale("log"); b.set_yticks([5, 10, 20, 50]); b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}")); b.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); b.set_xticks(range(len(labels)), labels); b.axhline(10, color=GRAY, ls="--", lw=0.9)
b.set_title("(b) Hardware, 10 instances per cell", fontsize=8.5, color=INK); b.legend(loc="upper left", fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "qaoa.pdf")); plt.close(fig)
print("figures written to", OUT)
