"""Development check (3 Nov 2026): alpha = 0.9 answers, with alpha-aware joint solver and rule.

Rule band with alpha: ask beats go when p > (tau_a+kappa)/(C*alpha); ask beats stop when
p < (tau_s - tau_a - kappa)/(tau_s + C*(1-alpha)); otherwise go below tau_s/(C+tau_s), else stop.
N = 6 noisy, 200 epochs, seeds 4 970 000+.
"""
import functools, os, sys
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, ROOT)
import pareto
from fleet_qubo import fleet_sim
from fleet_qubo.instances import Instance
from fleet_qubo.classical import exhaustive
A = 0.9
pareto.EPOCH_SEED = 4_970_000
pareto.run_fleet = functools.partial(fleet_sim.run_fleet, answer_accuracy=A)

def band(kappa):
    ask, gs = pareto.TAU_A + kappa, pareto.TAU_S / (pareto.C + pareto.TAU_S)
    lo, hi = ask / (pareto.C * A), (pareto.TAU_S - ask) / (pareto.TAU_S + pareto.C * (1 - A))
    return (lo, hi) if lo < hi else (gs, gs)
pareto.band = band

def joint(kappa, q):
    def solve(ps, idx):
        return exhaustive(Instance(p=np.array(ps), B=len(ps), q=q, C=pareto.C, tau_s=pareto.TAU_S,
                                   tau_a=pareto.TAU_A, kappa=kappa, alpha=A))["actions"]
    return solve
pareto.joint = joint
pareto.methods = lambda: [("indep", k, 0.0) for k in (0.5, 1.5, 3.0)] + [("jq", 1.5, 1.5), ("jq", 0.5, 0.0)]

if __name__ == "__main__":
    from multiprocessing import Pool
    jobs = [("noisy", cal, list(e), 6, 1.0) for cal in ("isotonic", "isotonic_dw") for e in np.array_split(np.arange(200), 2)]
    with Pool(2) as p:
        d = pd.DataFrame([r for c in p.map(pareto.task, jobs) for r in c])
    k = ["calibration", "kind", "kappa", "q"]
    c = d[d.crossing == 1]
    out = pd.DataFrame({"crossing": c.groupby(k).size(), "collisions": c.groupby(k).collision.sum(),
                        "q_per_epoch": d.groupby(k).n_asks.sum() / 200, "delay": d.groupby(k).delay.mean()}).reset_index()
    out.to_csv(os.path.join(ROOT, "results", "dev_alpha_aware.csv"), index=False)
    print(out.round(3).to_string())
