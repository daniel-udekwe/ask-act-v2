"""Parameter trace of the final H2 QAOA runs (for the paper's figures; no new results).

Repeats scripts/final_qaoa.py exactly (same instances, seeds, restarts, INTERP schedule) and records
the optimised angles and objective at every depth, plus the COBYLA objective history of the best
restart. Checks that the depth-3 angles equal those stored in results/final/qaoa_h2.csv.
Writes results/final/qaoa_trace.csv and results/final/qaoa_history.csv.
"""
import os, sys, json
import numpy as np, pandas as pd
from scipy.optimize import minimize
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import qaoa_variants as qv
from fleet_qubo.pool import ScenarioPool
from fleet_qubo.qubo import build_qubo
from fleet_qubo.qaoa import QaoaProblem, interp, objective
import fleet_qubo.qaoa as Q

SEED = 8_200_000
qv.SEED = SEED
pool = ScenarioPool(os.path.join(ROOT, "results", "final", "deadline_probs.csv"))
ref = pd.read_csv(os.path.join(ROOT, "results", "final", "qaoa_h2.csv"))
rows, hist = [], []

# wrap COBYLA to keep each restart's history; optimise() keeps the best restart
_orig = Q.minimize
def logged(fun, x0, args=(), **kw):
    h = []
    res = _orig(lambda x, *a: (h.append(fun(x, *a)) or h[-1]), x0, args=args, **kw)
    res.history = h
    return res
Q.minimize = logged

def optimise_logged(prob, depth, init, restarts, seed):
    rng = np.random.default_rng(seed)
    starts = [] if init is None else [init]
    while len(starts) < restarts:
        starts.append(np.concatenate([rng.uniform(0, 0.8, depth), rng.uniform(0, 0.8, depth)]))
    best = None
    for x0 in starts:
        res = logged(objective, x0, args=(prob, None, None), method="COBYLA", options={"maxiter": 400, "rhobeg": 0.2})
        if best is None or res.fun < best.fun:
            best = res
    return best.x, float(best.fun), best.history

for N in (4, 6, 8):
    for k in range(20):
        inst = qv.instance(pool, N, k)
        prob = QaoaProblem(build_qubo(inst, "slack"), inst)
        params = None
        for p in (1, 2, 3):
            params, f, h = optimise_logged(prob, p, interp(params) if params is not None else None, 3, SEED + k)
            pr = np.abs(Q.qaoa_state(params, prob)) ** 2
            rows.append(dict(N=N, instance=k, depth=p, objective=f, p_opt=float(pr[prob.state_opt].sum()),
                             gammas=json.dumps(list(np.round(params[:p], 6))), betas=json.dumps(list(np.round(params[p:], 6)))))
            hist += [dict(N=N, instance=k, depth=p, it=i, objective=v) for i, v in enumerate(h)]
        stored = np.array(eval(ref[(ref.N == N) & (ref.instance == k)].params.iloc[0].replace("np.float64", "")))
        assert np.allclose(stored, np.round(params, 5), atol=1e-5), (N, k)
        print(N, k, "ok", flush=True)
pd.DataFrame(rows).to_csv(os.path.join(ROOT, "results", "final", "qaoa_trace.csv"), index=False)
pd.DataFrame(hist).to_csv(os.path.join(ROOT, "results", "final", "qaoa_history.csv.gz"), index=False)
print("finished")
