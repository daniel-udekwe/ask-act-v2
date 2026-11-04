"""Fig.: evolution of QAOA parameters and output (from results/final/qaoa_trace.csv, qaoa_history.csv.gz)."""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
exec(open(os.path.join(ROOT, "scripts", "make_paper_figures.py")).read().split("# Fig. 2")[0])  # style + colours
R, OUT = os.path.join(ROOT, "results", "final"), os.path.join(ROOT, "paper", "figures")
t = pd.read_csv(os.path.join(R, "qaoa_trace.csv"))
h = pd.read_csv(os.path.join(R, "qaoa_history.csv.gz"))
COL = {4: AQUA, 6: BLUE, 8: ORANGE}
fig, ax = plt.subplots(2, 2, figsize=(7.0, 5.0))
# (a) angle schedules at depth 3
a = ax[0, 0]
d3 = t[t.depth == 3]
for N in (4, 6, 8):
    G = np.array([json.loads(x) for x in d3[d3.N == N].gammas]); B = np.array([json.loads(x) for x in d3[d3.N == N].betas])
    l = np.arange(1, 4)
    dx = {4: -0.08, 6: 0, 8: 0.08}[N]
    for M, fmt, lab, mfc in ((G, "-o", "γ", COL[N]), (B, "--s", "β", "white")):
        med = np.median(M, 0); lo_, hi_ = np.percentile(M, [25, 75], 0)
        a.errorbar(l + dx, med, yerr=[med - lo_, hi_ - med], fmt=fmt, color=COL[N], ms=4, mfc=mfc, capsize=2, lw=1.2, elinewidth=0.8, label=f"{lab}, N = {N}")
a.set_xticks([1, 2, 3]); a.set_xlabel("Layer l (depth p = 3)"); a.set_ylabel("Optimized angle (rad)")
a.set_title("(a) Angle schedules at p = 3 (median, IQR)", fontsize=8.5, color=INK)
a.legend(fontsize=6.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
# (b) probability on the optimum vs depth
b = ax[0, 1]
for N in (4, 6, 8):
    x = t[t.N == N]; m = x.groupby("depth").p_opt.median(); rnd = 3.0 ** -N if False else None
    b.plot(m.index, m.values * 4.0 ** N, "-o", color=COL[N], ms=4, label=f"N = {N}")
    q = x.groupby("depth").p_opt.quantile([0.25, 0.75]).unstack() * 4.0 ** N
    b.fill_between(q.index, q[0.25], q[0.75], color=COL[N], alpha=0.12, lw=0)
for N in (4, 6, 8):
    b.axhline(2 ** N, color=COL[N], ls=":", lw=0.9)
    b.text(3.05, 2 ** N, f"$2^{{{N}}}$", color=INK, fontsize=7, va="center")
b.set_yscale("log"); b.set_xticks([1, 2, 3]); b.set_xlabel("Depth p"); b.set_xlim(0.85, 3.3)
b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
b.set_ylabel("Lift over uniform sampling"); b.legend(fontsize=7, loc="upper left")
b.set_title("(b) Probability on the optimum as depth grows", fontsize=8.5, color=INK)
# (c) COBYLA convergence for the first instance of each size, depths 1-3 in sequence
c = ax[1, 0]
for N in (4, 6, 8):
    off = 0
    for p in (1, 2, 3):
        y = h[(h.N == N) & (h.instance == 0) & (h.depth == p)].objective.to_numpy()
        yb = np.minimum.accumulate(y)
        c.plot(np.arange(off, off + len(y)), yb, color=COL[N], lw=1.3, label=f"N = {N}" if p == 1 else None)
        if N == 8: c.axvline(off, color=GRAY, lw=0.6, ls=":")
        off += len(y)
c.set_xlabel("COBYLA evaluations (best restart; p = 1, 2, 3 in sequence)"); c.set_ylabel(r"Best $F_p$ so far")
c.set_title("(c) Convergence, first instance of each size", fontsize=8.5, color=INK); c.legend(fontsize=7)
# (d) probability mass on the halt subspace (every robot asks or stops)
d = ax[1, 1]
st = pd.read_csv(os.path.join(R, "qaoa_structure.csv"))
for N in (4, 6, 8):
    x = st[st.N == N].groupby("depth").halt_mass
    m, q1, q3 = x.median(), x.quantile(0.25), x.quantile(0.75)
    d.plot(m.index, m.values, "-o", color=COL[N], ms=4, label=f"N = {N}")
    d.fill_between(m.index, q1, q3, color=COL[N], alpha=0.15, lw=0)
    d.plot([1, 3], [2.0 ** -N] * 2, ":", color=COL[N], lw=0.9)
d.set_yscale("log"); d.set_xticks([1, 2, 3]); d.set_xlabel("Depth p"); d.set_ylabel("Probability on halt states")
d.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
d.text(1.05, 2.0 ** -8 * 1.4, "dotted: uniform sampling", fontsize=7, color=INK)
d.set_title("(d) Mass on states where every robot halts", fontsize=8.5, color=INK); d.legend(fontsize=7, loc="center right")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "qaoa_params.pdf")); plt.close(fig)
print("written")
