"""Fig. (post hoc): QAOA probability on the all-halt states, against uniform sampling and the optimum."""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
exec(open(os.path.join(ROOT, "scripts", "make_paper_figures.py")).read().split("# Fig. 2")[0])
import qaoa_variants as qv
from fleet_qubo.pool import ScenarioPool
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem, qaoa_state
R, OUT = os.path.join(ROOT, "results", "final"), os.path.join(ROOT, "paper", "figures")
qv.SEED = 8_200_000
pool = ScenarioPool(os.path.join(R, "deadline_probs.csv"))
tr = pd.read_csv(os.path.join(R, "qaoa_trace.csv")); bl = pd.read_csv(os.path.join(R, "qaoa_baselines.csv"))
N, K = 4, 0
inst = qv.instance(pool, N, K); prob = QaoaProblem(build_qubo(inst, "slack"), inst)
idx = np.arange(1 << (2 * N)); a_ = idx & ((1 << N) - 1); s_ = idx >> N
halt = np.flatnonzero((a_ ^ s_) == (1 << N) - 1)
halt = halt[np.argsort(prob.state_cost[halt])]
lab = ["".join("A" if (a_[h] >> i) & 1 else "S" for i in range(N)) for h in halt]
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw=dict(width_ratios=[1.7, 1]))
x = np.arange(len(halt)); w = 0.2
ax.bar(x - 1.5 * w, np.full(len(halt), 4.0 ** -N), w, color=GRAY, label="uniform (all states)")
for j, (p, col) in enumerate(((1, AQUA), (2, BLUE), (3, ORANGE))):
    r = tr[(tr.N == N) & (tr.instance == K) & (tr.depth == p)].iloc[0]
    pr = np.abs(qaoa_state(np.array(json.loads(r.gammas) + json.loads(r.betas)), prob)) ** 2
    ax.bar(x + (j - 0.5) * w, pr[halt], w, color=col, label=f"QAOA p = {p}")
ax.axhline(2.0 ** -N * 0.97, color=INK, ls=":", lw=0.9)
ax.text(len(halt) - 0.5, 2.0 ** -N * 1.03, "uniform over halt states", ha="right", va="bottom", fontsize=6.5, color=INK)
ax.plot(0, 0.071, "*", color=INK, ms=7); ax.text(0.35, 0.071, "optimum", fontsize=7, color=INK, va="center")
ax.set_xticks(x, lab, rotation=90, fontsize=6.5); ax.set_ylabel("Probability")
ax.set_xlabel("Halt states ranked by cost (A = ask, S = stop, robots 1-4)")
ax.set_title(f"(a) One N = 4 instance: the 16 states where every robot halts", fontsize=8.5, color=INK)
ax.legend(fontsize=6.5, ncol=2, loc="upper right"); ax.set_ylim(0, 0.11)
for i, N_ in enumerate((4, 6, 8)):
    b = bl[bl.N == N_]
    for j, p in enumerate((1, 2, 3)):
        v = b[f"qaoa_p{p}_cond"] / b.uniform_halt_cond
        bx.plot(i + (j - 1) * 0.22 + np.random.default_rng(j).uniform(-0.05, 0.05, len(v)), v, "o",
                color=(AQUA, BLUE, ORANGE)[j], ms=2.8, alpha=0.8, label=f"p = {p}" if i == 0 else None)
bx.axhline(1, color=INK, ls=":", lw=0.9); bx.text(-0.45, 0.63, "dotted: uniform over halt states", ha="left", fontsize=6.5, color=INK)
bx.set_xticks([0, 1, 2], ["N = 4", "N = 6", "N = 8"]); bx.set_ylim(0.6, 1.5)
bx.set_ylabel("P(optimum | halt) / uniform")
bx.set_title("(b) All 60 final instances", fontsize=8.5, color=INK); bx.legend(fontsize=6.5, loc="upper left")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "qaoa_halt.pdf")); plt.close(fig)
print("written")
