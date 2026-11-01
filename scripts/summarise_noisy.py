"""Summarise results/noisy_qaoa.csv into results/noisy_summary.md."""
import pandas as pd

d = pd.read_csv("results/noisy_qaoa.csv")
g = d.groupby(["N", "layout", "encoding", "depth", "sim"]).agg(
    qubits=("qubits", "first"), cz_gates=("two_qubit_gates", "mean"),
    p_opt=("p_opt", "mean"), random_p_opt=("random_p_opt", "mean"),
    p_feasible=("p_feasible", "mean"), random_p_feasible=("random_p_feasible", "mean"),
    found_opt=("found_opt", "mean")).reset_index()
w = g.pivot_table(index=["N", "layout", "encoding", "depth", "qubits", "cz_gates", "random_p_opt"],
                  columns="sim", values=["p_opt", "p_feasible"]).reset_index()
w.columns = ["_".join(c).strip("_") for c in w.columns]
w["p_opt_retained"] = w.p_opt_kingston_noise / w.p_opt_noiseless
w["lift_noisy"] = w.p_opt_kingston_noise / w.random_p_opt
txt = ("# QAOA under the ibm_kingston noise model\n\n"
       "Real-probability instances (noisy tracking, decision-aware calibration, dev seeds), "
       "N = 4: 8 instances at 4000 shots; N = 6 none: 3 instances (1 at 4000, 2 at 2000 shots); N = 6 single corridor: 3 instances at 2000 shots, depths 1-2. Parameters trained noiselessly. Retained = noisy p_opt / noiseless p_opt; "
       "lift = noisy p_opt / uniform random.\n\n" + w.round(4).to_markdown(index=False) + "\n")
open("results/noisy_summary.md", "w").write(txt)
print(txt)
