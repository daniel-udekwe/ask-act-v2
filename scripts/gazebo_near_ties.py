"""Gazebo v2 diagnosis: joint-mode action disagreements and the extra cost of the Gazebo assignment
under the offline probabilities. Usage: python scripts/gazebo_near_ties.py <unzipped diag dir>"""
import sys, os, json, numpy as np, pandas as pd
sys.path[:0] = ["/home/claude/daniel-udekwe/turtlebot3-ask_or_act", "/home/claude/fleet_qubo", "/home/claude/fleet_qubo/fleet_gazebo"]
import generate_scenarios as gs, ped_traj, policy as P, simulate_policies as sp
from fleet_qubo.fleet_sim import run_fleet, make_policy_class
from fleet_qubo.instances import Instance
from fleet_qubo.classical import exhaustive
from epochs import build_epoch, band
FP = make_policy_class(P.AskOrActPolicy)
env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at, ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
D = sys.argv[1]; lo, hi = band(1.5)
res = pd.read_csv(os.path.join(D, "results.csv")); res = res[res.method == "joint"]
res = res.sort_values("attempt").drop_duplicates(["epoch", "condition", "robot"], keep="last")
solve = lambda ps, idx: exhaustive(Instance(p=np.array(ps), B=len(ps), q=1.5, C=100.0, tau_s=10.0, tau_a=1.5, kappa=1.5))["actions"]
U = lambda p: np.array([100 * p, 10 * (1 - p), 3.0])     # go, stop, ask unary costs (alpha = 1)
rows = []
for e in range(20):
  for cond in ("nominal", "noisy"):
    labels, shifts = build_epoch("results/deadline_probs.csv", cond, 4, 4_700_000 + e)
    model, cal = P.load_predictor("predictor/intent_model.pkl", "mlp", "isotonic_dw", cond)
    pols = [FP(model, cal, mode="joint", true_intent=l["intent"], p_low=lo, p_high=hi) for l in labels]
    off, _, _ = run_fleet(labels, pols, gs.CONDITIONS[cond]["noise"], shifts, env, joint=solve)
    for r in res[(res.epoch == e) & (res.condition == cond)].itertuples():
        ga = json.loads(r.assigned).get("1", -1) if isinstance(r.assigned, str) else -1
        sa = off[r.robot]["action"]
        p = pols[r.robot].request[1] if pols[r.robot].request else np.nan
        rows.append(dict(cond=cond, e=e, i=r.robot, gz=ga, sim=sa, p_sim=p,
                         extra=(U(p)[ga] - U(p)[sa]) if (ga in (0, 1, 2) and sa in (0, 1, 2) and p == p) else np.nan))
o = pd.DataFrame(rows); o["agree"] = o.gz == o.sim
print(o.groupby("cond").agree.mean().round(3))
dis = o[~o.agree]; print(len(dis), "disagreements"); print(dis.round(3).to_string())
from fleet_qubo.instances import true_cost
ep = []
for (c, e), g in o.groupby(["cond", "e"]):
    g = g[(g.gz >= 0) & (g.sim >= 0) & g.p_sim.notna()]
    if not len(g): continue
    inst = Instance(p=g.p_sim.to_numpy(), B=len(g), q=1.5, C=100.0, tau_s=10.0, tau_a=1.5, kappa=1.5)
    ep.append(dict(cond=c, e=e, extra=true_cost(inst, g.gz.to_numpy()) - true_cost(inst, g.sim.to_numpy()), agree=(g.gz == g.sim).all()))
ep = pd.DataFrame(ep)
print(ep.groupby("cond").extra.describe().round(2))
print("epochs with extra <= 5:", (ep.extra <= 5).mean(), " <= 3:", (ep.extra <= 3).mean())
print(ep[ep.extra > 3])
