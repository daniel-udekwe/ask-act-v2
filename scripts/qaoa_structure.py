"""Post-hoc (exploratory): what structure does the trained QAOA state learn?

For every final H3 instance and depth, computes the probability mass on the 'halt' subspace
(each robot either asks or stops: a_i + s_i = 1), how uniform the state is inside it (total
variation distance from uniform), whether the optimum lies in it, and the probability ratio
between the optimum and the mean halt state. Writes results/final/qaoa_structure.csv.
"""
import os, sys, json
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import qaoa_variants as qv
from fleet_qubo.pool import ScenarioPool
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem, qaoa_state
qv.SEED = 8_200_000
pool = ScenarioPool(os.path.join(ROOT, "results", "final", "deadline_probs.csv"))
t = pd.read_csv(os.path.join(ROOT, "results", "final", "qaoa_trace.csv"))
rows = []
for N in (4, 6, 8):
    idx = np.arange(1 << (2 * N)); a = idx & ((1 << N) - 1); s = idx >> N
    halt = (a ^ s) == (1 << N) - 1
    for k in range(20):
        inst = qv.instance(pool, N, k); prob = QaoaProblem(build_qubo(inst, "slack"), inst)
        for p in (1, 2, 3):
            r = t[(t.N == N) & (t.instance == k) & (t.depth == p)].iloc[0]
            pr = np.abs(qaoa_state(np.array(json.loads(r.gammas) + json.loads(r.betas)), prob)) ** 2
            inside = pr[halt] / pr[halt].sum()
            rows.append(dict(N=N, instance=k, depth=p, halt_mass=pr[halt].sum(),
                             tv_from_uniform=0.5 * np.abs(inside - 1 / halt.sum()).sum(),
                             opt_in_halt=bool(halt[prob.state_opt].all()),
                             opt_over_mean_halt=pr[prob.state_opt].sum() / pr[halt].mean(),
                             lift=pr[prob.state_opt].sum() * 4 ** N))
d = pd.DataFrame(rows)
d.to_csv(os.path.join(ROOT, "results", "final", "qaoa_structure.csv"), index=False)
print(d.groupby(["N", "depth"]).agg(halt_mass=("halt_mass", "median"), tv=("tv_from_uniform", "median"),
      opt_in_halt=("opt_in_halt", "mean"), opt_ratio=("opt_over_mean_halt", "median"), lift=("lift", "median")).round(3))
