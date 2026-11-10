"""Post hoc (review): QAOA against stronger baselines on the 60 final H3 instances.

Probability of returning the optimum, and that probability conditional on the all-halt subspace
(every robot asks or stops), for: uniform sampling over all states, over feasible states, and over
all-halt states; QAOA at depths 1-3 (from results/final/qaoa_trace.csv); a greedy allocation
(exact for the queue formulation, see below); simulated annealing (one restart of 1,000 sweeps,
success rate over 50 seeds, and 32 restarts); and exhaustive search.

Greedy allocation: each robot's best non-ask action costs b_i = min(C p_i, tau_s (1 - p_i)); asking
saves g_i = b_i - L_i(ask). With k askers the queue adds q k (k - 1) / 2, so for any k the best
askers are the k largest g_i, and the optimum is found by sorting g and scanning k = 0..N.
Writes results/final/qaoa_baselines.csv.
"""
import os, sys, json
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import qaoa_variants as qv
from fleet_qubo.pool import ScenarioPool
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem
from fleet_qubo.classical import exhaustive, simulated_annealing
from fleet_qubo.instances import true_cost


def greedy(inst):
    U = inst.unary_costs(); base = U[:, :2].min(axis=1); act = U[:, :2].argmin(axis=1)
    g = base - U[:, 2]; order = np.argsort(-g)
    best_k, best = 0, 0.0
    for k in range(1, inst.N + 1):
        v = g[order[:k]].sum() - inst.q * k * (k - 1) / 2
        if v > best + 1e-12:
            best, best_k = v, k
    act = act.copy(); act[order[:best_k]] = 2
    return act


if __name__ == "__main__":
    qv.SEED = 8_200_000
    pool = ScenarioPool(os.path.join(ROOT, "results", "final", "deadline_probs.csv"))
    st = pd.read_csv(os.path.join(ROOT, "results", "final", "qaoa_structure.csv"))
    tr = pd.read_csv(os.path.join(ROOT, "results", "final", "qaoa_trace.csv"))
    rows = []
    rng = np.random.default_rng(0)
    for _ in range(2000):                                 # greedy is exact: random check
        n = int(rng.integers(1, 7)); from fleet_qubo.instances import Instance
        inst = Instance(p=rng.uniform(0, 1, n), B=n, q=1.5, C=100.0, tau_s=10.0, tau_a=1.5, kappa=1.5)
        assert abs(true_cost(inst, greedy(inst)) - exhaustive(inst)["cost"]) < 1e-9
    for N in (4, 6, 8):
        for k in range(20):
            inst = qv.instance(pool, N, k); prob = QaoaProblem(build_qubo(inst, "slack"), inst)
            ex = exhaustive(inst); opt = ex["cost"]
            r = dict(N=N, instance=k, uniform_all=4.0 ** -N, uniform_feasible=3.0 ** -N, uniform_halt=2.0 ** -N,
                     uniform_halt_cond=2.0 ** -N, greedy=float(abs(true_cost(inst, greedy(inst)) - opt) < 1e-9), exact=1.0)
            for p in (1, 2, 3):
                s = st[(st.N == N) & (st.instance == k) & (st.depth == p)].iloc[0]
                pt = tr[(tr.N == N) & (tr.instance == k) & (tr.depth == p)].iloc[0]
                r[f"qaoa_p{p}"] = pt.p_opt
                r[f"qaoa_p{p}_cond"] = pt.p_opt / s.halt_mass
            q_ = build_qubo(inst, "slack")
            r["sa_1restart"] = np.mean([abs(simulated_annealing(q_, inst, restarts=1, seed=s_)["cost"] - opt) < 1e-9 for s_ in range(50)])
            r["sa_32restarts"] = float(abs(simulated_annealing(q_, inst, seed=1)["cost"] - opt) < 1e-9)
            rows.append(r); print(N, k, flush=True)
    d = pd.DataFrame(rows); d.to_csv(os.path.join(ROOT, "results", "final", "qaoa_baselines.csv"), index=False)
    print(d.groupby("N").median().round(4).T.to_string())
