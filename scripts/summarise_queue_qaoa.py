"""Summarise results/queue_qaoa.csv (noiseless) and results/queue_qaoa_noisy.csv (Kingston noise)."""
import os

import pandas as pd

L = ["# QAOA on the queue formulation against the budget ablation (month 4, development seeds)", "",
     "Real-probability instances (noisy tracking, decision-aware calibration). Each formulation is "
     "scored against its own exact optimum. Lift = probability on the optimum / uniform random.", ""]

d = pd.read_csv("results/queue_qaoa.csv")
d["lift"] = d.p_opt / d.random_p_opt
d["feasible_cost_gap"] = (d.expected_feasible_cost - d.opt_cost) / d.opt_cost.abs()
g = d.groupby(["N", "formulation", "depth"]).agg(
    instances=("instance", "nunique"), qubits=("qubits", "first"),
    ground_state_ok=("ground_state_ok", "mean"), p_opt=("p_opt", "mean"), lift_median=("lift", "median"),
    p_feasible=("p_feasible", "mean"), random_p_feasible=("random_p_feasible", "mean"),
    feasible_cost_gap=("feasible_cost_gap", "median")).reset_index()
L += ["## Noiseless (1,024 shots)", "",
      "Feasible cost gap = median relative gap of the expected cost over feasible samples to the optimum.", "",
      g.round(4).to_markdown(index=False), ""]

if os.path.exists("results/queue_qaoa_noisy.csv"):
    n = pd.read_csv("results/queue_qaoa_noisy.csv")
    n["lift"] = n.p_opt / n.random_p_opt
    h = n.groupby(["N", "formulation", "depth"]).agg(
        instances=("instance", "nunique"), qubits=("qubits", "first"), cz_gates=("cz_gates", "mean"),
        p_opt_noiseless=("noiseless_p_opt", "mean"), p_opt_noisy=("p_opt", "mean"), lift_noisy=("lift", "median"),
        p_feasible_noiseless=("noiseless_p_feasible", "mean"), p_feasible_noisy=("p_feasible", "mean")).reset_index()
    L += ["## Under the ibm_kingston noise model (2,000 shots, parameters trained noiselessly)", "",
          h.round(4).to_markdown(index=False), ""]

open("results/queue_qaoa_summary.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
