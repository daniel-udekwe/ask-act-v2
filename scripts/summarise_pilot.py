"""Summarise results/pilot.csv into results/pilot_summary.md."""
import pandas as pd

df = pd.read_csv("results/pilot.csv")
q = df[df.solver.str.startswith("qaoa")].copy()
c = df[~df.solver.str.startswith("qaoa")].copy()
q["lift_p_opt"] = q.p_opt / q.random_p_opt
q["lift_p_feas"] = q.p_feasible / q.random_p_feasible

lines = ["# Month-1 pilot (noiseless, development seeds 3000-3009)", ""]

lines += ["## QAOA", "",
          "Lift = probability QAOA puts on the optimum (or on feasible states) divided by that of uniform random sampling.", ""]
g = q.groupby(["N", "layout", "solver", "depth"]).agg(
    qubits=("n_qubits", "first"),
    ground_state_ok=("ground_state_ok", "mean"),
    p_opt=("p_opt", "mean"),
    lift_p_opt=("lift_p_opt", "median"),
    p_feasible=("p_feasible", "mean"),
    lift_p_feas=("lift_p_feas", "median"),
    found_opt=("found_opt", "mean"),
    random_found_opt=("random_found_opt", "mean"),
    within_5pct=("within_5pct", "mean"),
).reset_index()
lines.append(g.round(3).to_markdown(index=False))

lines += ["", "## Classical baselines", "", "Share of instances solved to optimality and median gap to the optimum.", ""]
h = c.groupby(["N", "layout", "solver"]).agg(
    found_opt=("found_opt", "mean"),
    median_gap=("best_sample_gap", "median"),
    max_gap=("best_sample_gap", "max"),
    mean_time_s=("time", "mean"),
).reset_index()
lines.append(h.round(4).to_markdown(index=False))

open("results/pilot_summary.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
