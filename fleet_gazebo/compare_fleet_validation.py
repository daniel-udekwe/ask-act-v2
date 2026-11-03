#!/usr/bin/env python3
"""
Compare Gazebo fleet epochs with the offline simulator on identical inputs.

For every (epoch, condition, method) in runs/results.csv, rebuild the epoch's labels and
start offsets, run fleet_qubo.fleet_sim.run_fleet with the same policy, operator and
solver, and compare robot by robot.

Pre-specified agreement criteria (to be frozen with the analysis plan):
  * collision outcome agrees for at least 95% of robot-runs
    (Ask or Act's single-robot validation reached 97.5%);
  * number of questions agrees for at least 90% of robot-runs;
  * joint mode: the assigned action agrees for at least 90% of robots.

Usage: python3 compare_fleet_validation.py [--runs runs] [--final]
Writes runs/comparison.csv and prints the agreement table.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
FLEET = os.path.dirname(HERE)
AOA = os.path.join(HOME, "ask_or_act")


def deadline_p(rows):
    """First smoothed probability at or inside the decision deadline (0.6 m ahead)."""
    for r in rows:
        t, hid, p, action, why, ahead, oy = r
        if p != "" and p is not None and float(ahead) <= 0.6:
            return float(p)
    return None


def gazebo_decisions(path):
    import csv as _csv
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [tuple(r.values()) for r in _csv.DictReader(f)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(HERE, "runs"))
    a = ap.parse_args()
    sys.path[:0] = [AOA, FLEET, HERE]
    import generate_scenarios as gs
    import ped_traj
    import policy as aoa_policy
    import simulate_policies as sp
    from fleet_qubo.fleet_sim import run_fleet, make_policy_class, DT
    from fleet_qubo.instances import Instance
    from fleet_qubo.classical import exhaustive
    from epochs import band
    from run_fleet_gazebo import KAPPA, Q

    FleetPolicy = make_policy_class(aoa_policy.AskOrActPolicy)
    env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at,
               ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
    model_file = os.path.join(AOA, "predictor", "intent_model.pkl")
    lo, hi = band(KAPPA)

    def solve(ps, idx):
        inst = Instance(p=np.array(ps), B=len(ps), q=Q, C=100.0, tau_s=10.0, tau_a=1.5, kappa=KAPPA)
        return exhaustive(inst)["actions"]

    g = pd.read_csv(os.path.join(a.runs, "results.csv"))
    g["collision"] = g.collision.astype(str).str.lower().eq("true")
    # rows from the patched runner carry "valid"; older rows get the same rules after the fact
    stuck = (g.outcome == "timed out") & (g.stopped_time == 0) & (g.n_asks == 0) & ~g.collision
    rule = ~(g.min_dist.isna() | stuck)
    if "valid" in g:
        flag = g.valid.astype(str).str.lower()
        g["valid"] = flag.eq("true").where(flag.isin(["true", "false"]), rule)
    else:
        g["valid"] = rule
    full = g.groupby(["epoch", "condition", "method"]).robot.transform("size") == g.N
    g["valid"] &= full & g.groupby(["epoch", "condition", "method"]).valid.transform("all")
    bad = g[~g.valid].drop_duplicates(["epoch", "condition", "method"])
    print(f"Infrastructure failures excluded: {len(bad)} epoch groups "
          f"({(~g.valid).sum()} robot-runs): {[f'{e}:{c}:{m}' for e, c, m in zip(bad.epoch, bad.condition, bad.method)]}")
    expected = g.drop_duplicates(["epoch", "condition"]).shape[0] * g.method.nunique()
    found = g.drop_duplicates(["epoch", "condition", "method"]).shape[0]
    if found < expected:
        print(f"Missing epoch groups (no results at all): {expected - found}")
    g = g[g.valid]
    rows = []
    for (e, cond, m), grp in g.groupby(["epoch", "condition", "method"]):
        tag = f"e{int(e):03d}_{cond}"
        labels = json.load(open(os.path.join(a.runs, f"{tag}_labels.json")))
        shifts = json.load(open(os.path.join(a.runs, f"{tag}_timing.json")))["shifts"]
        model, cal = aoa_policy.load_predictor(model_file, "mlp", "isotonic_dw", cond)
        mode = "joint" if m == "joint" else "independent"
        pols = [FleetPolicy(model, cal, mode=mode, true_intent=l["intent"], p_low=lo, p_high=hi) for l in labels]
        off, _, _ = run_fleet(labels, pols, gs.CONDITIONS[cond]["noise"], shifts, env,
                              joint=solve if mode == "joint" else None)
        for r in grp.itertuples():
            o, lab = off[r.robot], labels[r.robot]
            free = lab["robot_delay"] + (gs.ROBOT["start"][0] - gs.ROBOT["goal"][0] - 0.15) / gs.ROBOT["speed"]
            assigned = json.loads(r.assigned).get("1", -1) if isinstance(r.assigned, str) else -1
            att = getattr(r, "attempt", 0)
            att = 0 if pd.isna(att) else int(att)            # rows from before the retry column existed
            ep_dir = os.path.join(a.runs, tag, m if att == 0 else f"{m}_retry{att}")
            p_gz = deadline_p(gazebo_decisions(os.path.join(ep_dir, f"decisions_{r.robot}.csv")))
            p_sim = deadline_p(pols[r.robot].decisions)
            rows.append(dict(epoch=e, condition=cond, method=m, robot=r.robot, intent=r.intent,
                             gz_collision=bool(r.collision), sim_collision=bool(o["collision"]),
                             gz_asks=r.n_asks, sim_asks=o["n_asks"],
                             gz_delay=r.duration - free, sim_delay=o["delay"],
                             gz_min_dist=r.min_dist, sim_min_dist=o["min_dist"],
                             gz_action=assigned, sim_action=o["action"], gz_p=p_gz, sim_p=p_sim))
    c = pd.DataFrame(rows)
    c.to_csv(os.path.join(a.runs, "comparison.csv"), index=False)
    c["col_agree"] = c.gz_collision == c.sim_collision
    c["ask_agree"] = c.gz_asks == c.sim_asks
    c["act_agree"] = c.gz_action == c.sim_action
    c["delay_diff"] = c.gz_delay - c.sim_delay
    t = c.groupby(["condition", "method"]).agg(
        robot_runs=("robot", "size"), collision_agreement=("col_agree", "mean"),
        question_agreement=("ask_agree", "mean"), action_agreement=("act_agree", "mean"),
        gz_collisions=("gz_collision", "sum"), sim_collisions=("sim_collision", "sum"),
        delay_diff_mean=("delay_diff", "mean"), delay_diff_sd=("delay_diff", "std"))
    t.loc[("all", "all"), :] = [len(c), c.col_agree.mean(), c.ask_agree.mean(),
                                c[c.method == "joint"].act_agree.mean(), c.gz_collision.sum(),
                                c.sim_collision.sum(), c.delay_diff.mean(), c.delay_diff.std()]
    pd.set_option("display.width", 160)
    print(t.round(3).to_string())
    # where do decisions diverge? compare the probability each robot had at its deadline
    c["dp"] = (c.gz_p - c.sim_p).abs()
    has = c.dp.notna()
    print(f"\nProbability at the deadline, Gazebo vs offline ({has.sum()} robot-runs with both):")
    print(f"  |difference| median {c.dp[has].median():.3f}, 90th percentile {c.dp[has].quantile(0.9):.3f}, "
          f"max {c.dp[has].max():.3f}; within 0.05: {(c.dp[has] <= 0.05).mean():.1%}")
    j = c[(c.method == "joint") & has]
    if len(j):
        print(f"  joint mode: actions agree {j.act_agree.mean():.1%} overall; "
              f"{j[j.dp <= 0.05].act_agree.mean():.1%} when |dp| <= 0.05, "
              f"{j[j.dp > 0.05].act_agree.mean():.1%} when |dp| > 0.05")
        eps = j.groupby(["epoch", "condition"]).agg(all_p_close=("dp", lambda x: (x <= 0.05).all()),
                                                    all_actions_agree=("act_agree", "all"))
        print(f"  epochs where every robot's p is within 0.05: {eps.all_p_close.mean():.1%}; "
              f"of those, all actions agree in {eps[eps.all_p_close].all_actions_agree.mean():.1%}")
    ok = (c.col_agree.mean() >= 0.95, c.ask_agree.mean() >= 0.90,
          c[c.method == "joint"].act_agree.mean() >= 0.90 if (c.method == "joint").any() else True)
    print("\nCriteria (collision >= 95%, questions >= 90%, joint actions >= 90%):",
          "MET" if all(ok) else f"NOT MET {ok}")


if __name__ == "__main__":
    main()
