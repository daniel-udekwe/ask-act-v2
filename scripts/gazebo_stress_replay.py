"""Post hoc: replay the Gazebo near-collision stress epochs offline and join them with the Gazebo results
(results/posthoc/gazebo_stress/comparison_local.csv). Usage: python scripts/gazebo_stress_replay.py <out.csv>"""
import os, sys, json, numpy as np, pandas as pd
ROOT="/home/claude/fleet_qubo"; AOA="/home/claude/daniel-udekwe/turtlebot3-ask_or_act"
sys.path[:0]=[AOA, ROOT, os.path.join(ROOT,"fleet_gazebo")]
import generate_scenarios as gs, ped_traj, policy as P, simulate_policies as sp
from fleet_qubo.fleet_sim import run_fleet, make_policy_class
from fleet_qubo.instances import Instance
from fleet_qubo.classical import exhaustive
from epochs import build_epoch, method_band
from run_fleet_gazebo import KAPPA, Q, STRESS_SEED
FP=make_policy_class(P.AskOrActPolicy)
env=dict(build_trajectory=ped_traj.build_trajectory,pose_at=ped_traj.pose_at,ROBOT=gs.ROBOT,COLLISION_DIST=sp.COLLISION_DIST)
solve=lambda ps,idx: exhaustive(Instance(p=np.array(ps),B=len(ps),q=Q,C=100.0,tau_s=10.0,tau_a=1.5,kappa=KAPPA))["actions"]
model,cal=P.load_predictor(os.path.join(ROOT,"predictor","intent_model.pkl"),"mlp","isotonic_dw","noisy")
g=pd.read_csv(os.path.join(ROOT,"results/posthoc/gazebo_stress/results.csv"))
pool=os.path.join(ROOT,"results","final","deadline_probs.csv")
rows=[]
for e in range(15):
    labels,shifts=build_epoch(pool,"noisy",4,STRESS_SEED+e,crossing_only=True)
    for m in ("always_go","risky","joint"):
        mode="joint" if m=="joint" else "independent"; lo,hi=method_band(m,KAPPA)
        pols=[FP(model,cal,mode=mode,true_intent=l["intent"],p_low=lo,p_high=hi) for l in labels]
        off,_,_=run_fleet(labels,pols,gs.CONDITIONS["noisy"]["noise"]*1.5,shifts,env,joint=solve if mode=="joint" else None,answer_accuracy=0.9)
        for i,o in enumerate(off):
            r=g[(g.epoch==e)&(g.method==m)&(g.robot==i)].iloc[0]
            assert r.scenario==labels[i]["id"]
            rows.append(dict(epoch=e,method=m,robot=i,family=r.family,gz_col=str(r.collision).lower()=="true",sim_col=bool(o["collision"]),
                gz_md=r.min_dist,sim_md=o["min_dist"],gz_asks=r.n_asks,sim_asks=o["n_asks"],gz_out=r.outcome,gz_dur=r.duration,sim_delay=o["delay"],sim_action=o["action"]))
c=pd.DataFrame(rows); c.to_csv(sys.argv[1],index=False)
print(c.groupby("method")[["gz_col","sim_col"]].sum())
