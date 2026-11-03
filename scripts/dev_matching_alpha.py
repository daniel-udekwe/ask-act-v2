"""H4 development matching (3 Nov 2026): alpha = 0.9, alpha-aware rule matched to the joint rate.

Joint: kappa = 1.5, q = 1.5, alpha = 0.9. Rule: alpha-aware band (see dev_alpha_aware.py); the band
closes at kappa = 6.68. N = 6 and 8, noisy, decision-aware, 500 epochs, seeds 4 980 000+.
Writes results/dev_matching_alpha.csv.
"""
import os
import numpy as np, pandas as pd
import dev_alpha_aware as daa          # patches pareto for alpha = 0.9
pareto = daa.pareto
pareto.EPOCH_SEED = 4_980_000
GRID = [4.0, 4.5, 5.0, 5.25, 5.5, 5.75, 6.0, 6.25, 6.5, 6.6]
pareto.methods = lambda: [("indep", k, 0.0) for k in GRID] + [("jq", 1.5, 1.5)]

if __name__ == "__main__":
    from multiprocessing import Pool
    jobs = [("noisy", "isotonic_dw", list(e), N, 1.0) for N in (6, 8) for e in np.array_split(np.arange(500), 4)]
    with Pool(2) as p:
        d = pd.DataFrame([r for c in p.map(pareto.task, jobs) for r in c])
    s = d.groupby(["N", "kind", "kappa"]).apply(lambda x: pd.Series({
        "questions": x.groupby("epoch").n_asks.sum().mean(),
        "collisions": x[x.crossing == 1].collision.sum(), "crossing": (x.crossing == 1).sum(),
        "delay_s": x.delay.mean()})).reset_index()
    s.to_csv(os.path.join(daa.ROOT, "results", "dev_matching_alpha.csv"), index=False)
    print(s.round(3).to_string())
    for N in (6, 8):
        j = s[(s.N == N) & (s.kind == "jq")].iloc[0]
        ind = s[(s.N == N) & (s.kind == "indep")].sort_values("questions")
        print(f"N = {N}: joint asks {j.questions:.3f}; matched kappa = {np.interp(j.questions, ind.questions, ind.kappa):.3f}")
