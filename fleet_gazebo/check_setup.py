#!/usr/bin/env python3
"""
Check that this machine can run the fleet Gazebo validation, before starting Gazebo.

Run after sourcing ROS 2 and the HuNavSim workspace:
  python3 check_setup.py
Prints PASS / FAIL per item and ends with an offline run of one fleet epoch.
"""
import importlib
import os
import re
import shutil
import sys

HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
FLEET = os.path.dirname(HERE)
AOA = os.path.join(HOME, "ask_or_act")
results = []


def check(name, ok, hint=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + ("" if ok or not hint else f"\n       -> {hint}"))
    return ok


def main():
    print(f"Python {sys.version.split()[0]} at {sys.executable}")
    check("Python 3.10 or newer", sys.version_info >= (3, 10), "use the system python3 that ROS 2 Humble uses")
    for mod in ("numpy", "pandas", "scipy", "sklearn"):
        try:
            m = importlib.import_module(mod)
            check(f"import {mod} ({getattr(m, '__version__', '?')})", True)
        except Exception as e:
            check(f"import {mod}", False, f"{e}; install with apt or pip as for Ask or Act")

    check("Ask or Act repository at ~/ask_or_act", os.path.isfile(os.path.join(AOA, "policy.py")),
          "clone or copy the Ask or Act code to ~/ask_or_act")
    model = os.path.join(AOA, "predictor", "intent_model.pkl")
    check("predictor at ~/ask_or_act/predictor/intent_model.pkl", os.path.isfile(model),
          "run build_dataset.py and train_predictor.py in ~/ask_or_act, as for the paper")
    pool = os.path.join(FLEET, "results", "deadline_probs.csv")
    check("development pool results/deadline_probs.csv", os.path.isfile(pool), "pull the repository again")

    sdf = os.path.join(HOME, "burger_novis.sdf")
    if check("robot model ~/burger_novis.sdf", os.path.isfile(sdf), "copy it from the Ask or Act setup"):
        txt = open(sdf).read()
        m = re.search(r"<odometry_source>\s*(\w+)\s*</odometry_source>", txt)
        src = m.group(1) if m else "not set (plugin default)"
        check(f"diff-drive odometry source: {src}", (m is None) or src in ("1", "world"),
              "odometry must be in world coordinates (odometry_source 1 / world), as in Ask or Act")
        check("diff-drive plugin present", "diff_drive" in txt, "the robot model needs the gazebo_ros diff-drive plugin")

    check("empty world /usr/share/gazebo-11/worlds/empty.world",
          os.path.isfile("/usr/share/gazebo-11/worlds/empty.world"), "install gazebo11 (Gazebo Classic)")
    check("gzserver on PATH", shutil.which("gzserver") is not None, "install Gazebo 11")
    check("ros2 on PATH", shutil.which("ros2") is not None, "source /opt/ros/humble/setup.bash")
    for mod in ("rclpy", "gazebo_msgs.srv", "hunav_msgs.msg", "nav_msgs.msg"):
        try:
            importlib.import_module(mod)
            check(f"import {mod}", True)
        except Exception as e:
            check(f"import {mod}", False, f"{e}; source ROS 2 and the HuNavSim workspace (install/setup.bash)")

    # offline epoch with this machine's model: proves the fleet code runs on these library versions
    try:
        sys.path[:0] = [AOA, FLEET, HERE]
        import numpy as np
        import generate_scenarios as gs
        import ped_traj
        import policy as aoa_policy
        import simulate_policies as sp
        from fleet_qubo.fleet_sim import run_fleet, make_policy_class
        from fleet_qubo.instances import Instance
        from fleet_qubo.classical import exhaustive
        from epochs import build_epoch, band, start_delays
        labels, shifts = build_epoch(pool, "noisy", 2, 4_700_000)
        model_, cal = aoa_policy.load_predictor(model, "mlp", "isotonic_dw", "noisy")
        FP = make_policy_class(aoa_policy.AskOrActPolicy)
        env = dict(build_trajectory=ped_traj.build_trajectory, pose_at=ped_traj.pose_at,
                   ROBOT=gs.ROBOT, COLLISION_DIST=sp.COLLISION_DIST)
        solve = lambda ps, idx: exhaustive(Instance(p=np.array(ps), B=len(ps), q=1.5, C=100.0, tau_s=10.0,
                                                    tau_a=1.5, kappa=1.5))["actions"]
        lo, hi = band(1.5)
        pols = [FP(model_, cal, mode="joint", true_intent=l["intent"], p_low=lo, p_high=hi) for l in labels]
        out, _, ep = run_fleet(labels, pols, gs.CONDITIONS["noisy"]["noise"], shifts, env, joint=solve)
        print("       smoke-test epoch 0 (noisy, joint), offline prediction:")
        for i, (l, o) in enumerate(zip(labels, out)):
            print(f"         robot {i}: {l['id']} ({l['intent']}), action {o['action']}, "
                  f"collision {o['collision']}, questions {o['n_asks']}, delay {o['delay']} s")
        print(f"         start delays after /fleet/go: {[round(d, 2) for d in start_delays(shifts)]} s")
        check("offline fleet epoch runs with this machine's model and libraries", True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        check("offline fleet epoch", False, f"{type(e).__name__}: {e} (send me this output)")

    print(f"\n{sum(results)} of {len(results)} checks passed." +
          (" Ready for the smoke test." if all(results) else " Fix the FAIL items first."))


if __name__ == "__main__":
    main()
