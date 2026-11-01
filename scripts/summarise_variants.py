"""Summarise QAOA variant results (results/qaoa_variants*.csv) into results/qaoa_variants_summary.md."""
import glob

import pandas as pd

d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("results/qaoa_variants*.csv"))], ignore_index=True)
d["lift"] = d.p_opt / d.random_p_opt
g = d.groupby(["N", "variant", "depth"]).agg(
    instances=("instance", "nunique"), qubits=("qubits", "first"),
    p_opt=("p_opt", "mean"), lift_median=("lift", "median"), p_feasible=("p_feasible", "mean"),
    feasible_cost_gap=("feasible_cost_gap", "median"), p_beats_heuristic=("p_beats_heuristic", "mean"),
    heuristic_gap=("heuristic_gap", "median"), found_opt_1024=("best_sample_gap", lambda x: (x <= 1e-9).mean()),
    secs=("secs", "mean")).reset_index()
best = d[d.depth == d.groupby("N").depth.transform("max")]
w = best.pivot_table(index=["N", "instance"], columns="variant", values="feasible_cost_gap")
wins = {v: float((w[v] == w.min(axis=1)).mean()) for v in w.columns}
L = ["# QAOA variants on the queue formulation (month 5, development seeds)", "",
     "κ = 1.5, q = 1.5, noisy tracking, decision-aware calibration. Noiseless statevector, 1,024 shots "
     "for the best-sample metric. Heuristic = each robot's own optimum, ignoring the queue (the warm "
     "start's source). p_beats_heuristic = probability of a feasible state strictly cheaper than the heuristic.",
     "", g.round(4).to_markdown(index=False), "",
     "Share of instances (deepest depth) where each variant has the lowest feasible expected cost: "
     + ", ".join(f"{k} {v:.2f}" for k, v in wins.items()) + "."]
open("results/qaoa_variants_summary.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
