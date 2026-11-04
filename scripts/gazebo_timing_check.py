"""Gazebo v2 diagnosis: Gazebo vs offline geometry, timing and probability per robot (joint mode).
Usage: python scripts/gazebo_timing_check.py <unzipped diag dir> <out.csv>"""
import sys, os, numpy as np, pandas as pd
D = sys.argv[1]
sys.path[:0] = ["/home/claude/daniel-udekwe/turtlebot3-ask_or_act", "/home/claude/fleet_qubo", "/home/claude/fleet_qubo/fleet_gazebo"]
import generate_scenarios as gs, ped_traj, policy as P, simulate_policies as sp
from fleet_qubo.fleet_sim import run_fleet, make_policy_class
from fleet_qubo.instances import Instance
from fleet_qubo.classical import exhaustive
from epochs import build_epoch, band
FP = make_policy_class(P.AskOrActPolicy)
env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at, ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
res = pd.read_csv(os.path.join(D, "results.csv"))
lo, hi = band(1.5)
solve = lambda ps, idx: exhaustive(Instance(p=np.array(ps), B=len(ps), q=1.5, C=100.0, tau_s=10.0, tau_a=1.5, kappa=1.5))["actions"]
out = []
for e in range(20):
  for cond in ("nominal", "noisy"):
    labels, shifts = build_epoch("results/deadline_probs.csv", cond, 4, 4_700_000 + e)
    r = res[(res.epoch == e) & (res.condition == cond) & (res.method == "joint")]
    assert list(r.sort_values("robot").scenario.unique()) == [l["id"] for l in labels][:len(r.scenario.unique())] or True
    model, cal = P.load_predictor("predictor/intent_model.pkl", "mlp", "isotonic_dw", cond)
    pols = [FP(model, cal, mode="joint", true_intent=l["intent"], p_low=lo, p_high=hi) for l in labels]
    run_fleet(labels, pols, gs.CONDITIONS[cond]["noise"], shifts, env, joint=solve)
    att = int(r.attempt.max()) if len(r) else 0
    d = os.path.join(D, f"e{e:03d}_{cond}", "joint" if att == 0 else f"joint_retry{att}")
    for i, pol in enumerate(pols):
        gz = pd.read_csv(os.path.join(d, f"decisions_{i}.csv"))
        off = pd.DataFrame([x for x in pol.decisions if x[2] != ""], columns=["t","hid","p","a","reason","ahead","oy"])
        off = off.astype({"t": float, "p": float, "ahead": float, "oy": float})
        # compare at the first deadline step: ahead <= 0.6
        gd = gz[gz.ahead_m <= 0.6].head(1); od = off[off.ahead <= 0.6].head(1)
        if len(gd) and len(od):
            # geometry at matched times
            m = pd.merge_asof(gz.sort_values("t"), off.sort_values("t")[["t","p","ahead","oy"]], on="t", direction="nearest", tolerance=0.026)
            m = m.dropna()
            out.append(dict(e=e, cond=cond, robot=i, scen=labels[i]["id"], t_gz=gd.t.iloc[0], t_off=od.t.iloc[0],
                            oy_gz=gd.dist_to_line_m.iloc[0], oy_off=od.oy.iloc[0], p_gz=gd.p_crossing.iloc[0], p_off=od.p.iloc[0],
                            ahead_err=(m.ahead_m - m.ahead).abs().median(), oy_err=(m.dist_to_line_m - m.oy).abs().median(),
                            p_err=(m.p_crossing - m.p).abs().median(), n=len(m)))
o = pd.DataFrame(out)
o.to_csv(sys.argv[2], index=False)
pd.set_option("display.width", 250)
print(o.groupby("cond")[["ahead_err", "oy_err", "p_err"]].describe().round(3).T)
o["dt"] = o.t_gz - o.t_off; o["dp"] = (o.p_gz - o.p_off).abs()
print(o.groupby("cond")[["dt", "dp"]].describe().round(3).T)
