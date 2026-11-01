#!/usr/bin/env python3
"""
Run fleet epochs in Gazebo: N TurtleBot3s on parallel lanes, one scripted pedestrian per
lane, one shared operator, and (joint mode) the joint solver at the decision deadline.

Per epoch and method: start gzserver on an empty world, spawn the robots (namespaced
/robot_<i>), start the pedestrians, the coordinator and the controllers, wait for every
robot to finish, record one row per robot, shut everything down.

Methods:
  indep   each robot's own cost-model rule (band from kappa), sharing the operator
  joint   queue-aware joint solver (exact), robots hold at the deadline for the epoch

Needs (on the ROS 2 Humble / Gazebo 11 machine used for Ask or Act):
  ~/ask_or_act        the Ask or Act repository, with predictor/intent_model.pkl
  ~/fleet_qubo        this repository, with results/deadline_probs.csv (development pool)
  ~/burger_novis.sdf  the robot model used by Ask or Act

Usage:
  python3 run_fleet_gazebo.py --epochs 0 --N 2 --gui              # smoke test, watch it
  python3 run_fleet_gazebo.py --N 4 --epochs 0-19                  # development validation
  python3 run_fleet_gazebo.py --final --N 4 --epochs 0-19          # after the freeze (final pool)
Resumable: finished (epoch, condition, method) groups in results.csv are skipped.
"""
import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
FLEET = os.path.dirname(HERE)
AOA = os.path.join(HOME, "ask_or_act")
ROBOT_SDF = os.path.join(HOME, "burger_novis.sdf")
STATE_PLUGIN = ('<plugin name="gazebo_ros_state" filename="libgazebo_ros_state.so">'
                '<ros><namespace>/</namespace></ros></plugin>')
GZ_PARAMS = os.path.join(HERE, "gazebo_params.yaml")
DEV_SEED, FINAL_SEED = 4_700_000, 8_700_000
KAPPA, Q, ACC = 1.5, 1.5, 1.0


def ensure_world():
    os.makedirs(os.path.join(HERE, "worlds"), exist_ok=True)
    dst = os.path.join(HERE, "worlds", "fleet_empty.world")
    if not os.path.exists(dst):
        src = open("/usr/share/gazebo-11/worlds/empty.world").read()
        j = src.index(">", src.index("<world")) + 1
        open(dst, "w").write(src[:j] + "\n    " + STATE_PLUGIN + src[j:])
    if not os.path.exists(GZ_PARAMS):
        open(GZ_PARAMS, "w").write("gazebo:\n  ros__parameters:\n    use_sim_time: true\n    publish_rate: 100.0\n")
    return dst


def quiet(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def kill_sim():
    quiet(["killall", "-9", "gzserver", "gzclient"])
    quiet(["pkill", "-9", "-f", "fleet_controller.py|fleet_pedestrians.py|fleet_coordinator.py"])


def stop(p):
    if p is None or p.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGINT)
        p.wait(timeout=10)
    except (subprocess.TimeoutExpired, ProcessLookupError):
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass


def run_epoch(labels, delays, cond, method, world, ep_dir, labels_file, a):
    from epochs import LANE, band
    N = len(labels)
    os.makedirs(ep_dir, exist_ok=True)
    logs = {n: open(os.path.join(ep_dir, f"{n}.log"), "w") for n in ("gazebo", "spawn", "nodes")}
    procs, ctrls = [], []
    kill_sim()
    time.sleep(1.0)
    lo, hi = band(KAPPA)
    try:
        procs.append(subprocess.Popen(["gzserver", world, "-s", "libgazebo_ros_init.so", "-s",
                                       "libgazebo_ros_factory.so", "--ros-args", "--params-file", GZ_PARAMS],
                                      stdout=logs["gazebo"], stderr=subprocess.STDOUT, start_new_session=True))
        if a.gui:
            procs.append(subprocess.Popen(["gzclient"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                          start_new_session=True))
        for i in range(N):
            subprocess.run(["ros2", "run", "gazebo_ros", "spawn_entity.py", "-entity", f"burger_{i}",
                            "-file", ROBOT_SDF, "-robot_namespace", f"/robot_{i}",
                            "-x", "2.9", "-y", str(0.1 + LANE * i), "-z", "0.05", "-Y", "3.14159",
                            "-timeout", "120"], stdout=logs["spawn"], stderr=subprocess.STDOUT,
                           timeout=180, check=True)
        common = ["-p", "use_sim_time:=true", "-p", f"labels_file:={labels_file}"]
        for i, lab in enumerate(labels):
            procs.append(subprocess.Popen(
                ["python3", os.path.join(HERE, "fleet_pedestrians.py"), "--ros-args", "-r", f"__ns:=/robot_{i}",
                 *common, "-p", f"aoa_dir:={AOA}", "-p", f"scenario_id:={lab['id']}",
                 "-p", f"lane_offset_y:={LANE * i}", "-p", f"model_name:=pedestrian_{i}"],
                stdout=logs["nodes"], stderr=subprocess.STDOUT, start_new_session=True))
        procs.append(subprocess.Popen(
            ["python3", os.path.join(HERE, "fleet_coordinator.py"), "--ros-args", *common,
             "-p", f"fleet_dir:={FLEET}", "-p", f"scenarios:={','.join(l['id'] for l in labels)}",
             "-p", f"mode:={'joint' if method == 'joint' else 'independent'}", "-p", f"kappa:={KAPPA}",
             "-p", f"q:={Q}", "-p", f"answer_accuracy:={a.accuracy}",
             "-p", f"log_file:={os.path.join(ep_dir, 'coordinator.json')}"],
            stdout=logs["nodes"], stderr=subprocess.STDOUT, start_new_session=True))
        time.sleep(4.0)
        for i, (lab, d) in enumerate(zip(labels, delays)):
            ctrls.append(subprocess.Popen(
                ["python3", os.path.join(HERE, "fleet_controller.py"), "--ros-args", "-r", f"__ns:=/robot_{i}",
                 "-p", "use_sim_time:=true", "-p", f"robot_index:={i}", "-p", f"scenario_id:={lab['id']}",
                 "-p", f"aoa_dir:={AOA}", "-p", f"fleet_dir:={FLEET}",
                 "-p", f"model_file:={os.path.join(AOA, 'predictor', 'intent_model.pkl')}",
                 "-p", f"odom_offset_y:={-LANE * i}", "-p", f"start_delay:={d:.3f}",
                 "-p", f"human_release_delay:={lab['release_delay']:.3f}",
                 "-p", f"robot_start_delay:={lab['robot_delay']:.3f}",
                 "-p", f"mode:={'joint' if method == 'joint' else 'independent'}",
                 "-p", f"calibration:=isotonic_dw", "-p", f"calib_condition:={cond}",
                 "-p", f"p_low:={lo}", "-p", f"p_high:={hi}",
                 "-p", f"obs_noise:={a.noise[cond]}", "-p", f"noise_seed:={lab['id']}",
                 "-p", f"true_intent:={lab['intent']}",
                 "-p", f"result_file:={os.path.join(ep_dir, f'robot_{i}.json')}",
                 "-p", f"decisions_file:={os.path.join(ep_dir, f'decisions_{i}.csv')}"],
                stdout=logs["nodes"], stderr=subprocess.STDOUT, start_new_session=True))
        t0 = time.time()
        while any(c.poll() is None for c in ctrls) and time.time() - t0 < a.timeout:
            time.sleep(1.0)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"   epoch failed: {e}")
    finally:
        for p in reversed(ctrls + procs):
            stop(p)
        for f in logs.values():
            f.close()
        kill_sim()
    out = []
    for i in range(N):
        path = os.path.join(ep_dir, f"robot_{i}.json")
        out.append(json.load(open(path)) if os.path.exists(path) else None)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--N", type=int, default=4)
    ap.add_argument("--epochs", default="0-19", help="e.g. 0-19 or 3")
    ap.add_argument("--conditions", nargs="+", default=["nominal", "noisy"])
    ap.add_argument("--methods", nargs="+", default=["indep", "joint"], choices=["indep", "joint"])
    ap.add_argument("--accuracy", type=float, default=ACC)
    ap.add_argument("--final", action="store_true", help="use the reserved final pool (after the freeze)")
    ap.add_argument("--out", default=os.path.join(HERE, "runs"))
    ap.add_argument("--timeout", type=float, default=600.0, help="wall-clock s per epoch")
    ap.add_argument("--gui", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, AOA)
    sys.path.insert(0, HERE)
    from generate_scenarios import CONDITIONS
    from epochs import build_epoch, start_delays, DT
    a.noise = {c: CONDITIONS[c]["noise"] for c in CONDITIONS}
    lo_hi = a.epochs.split("-")
    epochs = range(int(lo_hi[0]), int(lo_hi[-1]) + 1)
    pool = os.path.join(FLEET, "results", "final" if a.final else "", "deadline_probs.csv")
    seed0 = FINAL_SEED if a.final else DEV_SEED
    world = ensure_world()
    os.makedirs(a.out, exist_ok=True)
    res_csv = os.path.join(a.out, "results.csv")
    cols = ["epoch", "condition", "method", "N", "robot", "scenario", "family", "intent", "shift_steps",
            "robot_delay", "outcome", "duration", "min_dist", "collision", "n_asks", "stopped_time",
            "assigned", "held_s", "fallback"]
    done = set()
    if os.path.exists(res_csv):
        done = {(int(r["epoch"]), r["condition"], r["method"]) for r in csv.DictReader(open(res_csv))}
    new = not os.path.exists(res_csv)
    with open(res_csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        for e in epochs:
            for cond in a.conditions:
                labels, shifts = build_epoch(pool, cond, a.N, seed0 + e)
                delays = start_delays(shifts)
                ep_tag = f"e{e:03d}_{cond}"
                labels_file = os.path.join(a.out, f"{ep_tag}_labels.json")
                json.dump(labels, open(labels_file, "w"), indent=1)
                json.dump(dict(shifts=shifts, delays=delays, seed=seed0 + e), open(
                    os.path.join(a.out, f"{ep_tag}_timing.json"), "w"))
                for m in a.methods:
                    if (e, cond, m) in done:
                        continue
                    print(f"epoch {e} {cond} {m}: {[l['id'] for l in labels]}", flush=True)
                    res = run_epoch(labels, delays, cond, m, world, os.path.join(a.out, ep_tag, m), labels_file, a)
                    for i, (lab, r) in enumerate(zip(labels, res)):
                        if r is None:
                            print(f"   robot {i}: no result; see {os.path.join(a.out, ep_tag, m)}")
                            continue
                        w.writerow(dict(epoch=e, condition=cond, method=m, N=a.N, robot=i, scenario=lab["id"],
                                        family=lab["family"], intent=lab["intent"], shift_steps=shifts[i],
                                        robot_delay=lab["robot_delay"], outcome=r["outcome"],
                                        duration=r["duration"], min_dist=r["min_dist"],
                                        collision=r["min_dist"] is not None and r["min_dist"] < 0.4,
                                        n_asks=r["n_asks"], stopped_time=r["stopped_time"],
                                        assigned=json.dumps(r["assigned"]), held_s=r["held_s"],
                                        fallback=r["fallback"]))
                    f.flush()
    print("Results in", res_csv)


if __name__ == "__main__":
    main()
