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
    a.plot(l, np.median(G, 0), "-o", color=COL[N], ms=4, label=f"γ, N = {N}")
    a.plot(l, np.median(B, 0), "--s", color=COL[N], ms=4, mfc="white", label=f"β, N = {N}")
    a.fill_between(l, *np.percentile(G, [25, 75], 0), color=COL[N], alpha=0.12, lw=0)
    a.fill_between(l, *np.percentile(B, [25, 75], 0), color=COL[N], alpha=0.12, lw=0)
a.set_xticks([1, 2, 3]); a.set_xlabel("Layer l (depth p = 3)"); a.set_ylabel("Optimized angle (rad)")
a.set_title("(a) Angle schedules (median, IQR; 20 instances)", fontsize=8.5, color=INK)
a.legend(fontsize=6.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
# (b) probability on the optimum vs depth
b = ax[0, 1]
for N in (4, 6, 8):
    x = t[t.N == N]; m = x.groupby("depth").p_opt.median(); rnd = 3.0 ** -N if False else None
    b.plot(m.index, m.values * 4.0 ** N, "-o", color=COL[N], ms=4, label=f"N = {N}")
    q = x.groupby("depth").p_opt.quantile([0.25, 0.75]).unstack() * 4.0 ** N
    b.fill_between(q.index, q[0.25], q[0.75], color=COL[N], alpha=0.12, lw=0)
b.set_yscale("log"); b.set_xticks([1, 2, 3]); b.set_xlabel("Depth p")
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
# (d) output distribution for one N = 6 instance
import qaoa_variants as qv
from fleet_qubo.pool import ScenarioPool
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem, qaoa_state
qv.SEED = 8_200_000
inst = qv.instance(ScenarioPool(os.path.join(R, "deadline_probs.csv")), 6, 0)
prob = QaoaProblem(build_qubo(inst, "slack"), inst)
feas = np.flatnonzero(prob.state_feas); order = feas[np.argsort(prob.state_cost[feas])][:40]
d = ax[1, 1]
for p, mk in ((1, "o"), (2, "s"), (3, "D")):
    r = t[(t.N == 6) & (t.instance == 0) & (t.depth == p)].iloc[0]
    pr = np.abs(qaoa_state(np.array(json.loads(r.gammas) + json.loads(r.betas)), prob)) ** 2
    d.plot(np.arange(1, 41), pr[order], mk + "-", color=[AQUA, BLUE, ORANGE][p - 1], ms=3, lw=0.8, label=f"p = {p}")
d.axhline(1 / 4 ** 6, color=GRAY, ls="--", lw=0.9); d.text(40, 1.3 / 4 ** 6, "uniform", ha="right", fontsize=7, color=INK)
d.set_yscale("log"); d.set_xlabel("Feasible states ranked by cost (1 = optimum)"); d.set_ylabel("Probability")
d.set_title("(d) Output distribution, N = 6 instance", fontsize=8.5, color=INK); d.legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "qaoa_params.pdf")); plt.close(fig)
print("written")
