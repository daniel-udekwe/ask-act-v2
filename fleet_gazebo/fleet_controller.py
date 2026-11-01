#!/usr/bin/env python3
"""
One fleet robot in Gazebo: the Ask or Act line controller, adapted for a fleet.

Differences from line_controller.py (Ask or Act), everything else is unchanged:
  * all topics are relative, so the node runs in its robot's namespace (/robot_<i>);
  * the robot drives its own lane, `odom_offset_y` maps the lane back to the Ask or Act frame;
  * the episode clock starts `start_delay` s after the coordinator's /fleet/go signal, so
    robots start at the same relative times as in the offline simulator;
  * questions go to the shared operator (/fleet/ask) instead of the pedestrian, and answers
    come back on `operator_answer`;
  * mode "independent": the unchanged Ask or Act threshold policy (band p_low-p_high);
    mode "joint": the fleet policy (fleet_qubo.fleet_sim): observe to the deadline, send a
    request on /fleet/request, hold, and follow the assignment from `assignment`.

Run by run_fleet_gazebo.py; by hand:
  python3 fleet_controller.py --ros-args -r __ns:=/robot_0 -p use_sim_time:=true -p robot_index:=0 ...
"""
import csv
import json
import math
import os
import random
import sys

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from hunav_msgs.msg import Agents
from std_msgs.msg import String

HOME = os.path.expanduser("~")
OBS_RATE = 10.0


def yaw_from_quat(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


class FleetController(Node):
    def __init__(self):
        super().__init__("fleet_controller")
        defaults = dict(
            robot_index=0, scenario_id="", aoa_dir=os.path.join(HOME, "ask_or_act"),
            fleet_dir=os.path.join(HOME, "fleet_qubo"),
            start_x=2.9, start_y=0.1, goal_x=-2.9, goal_y=0.0, odom_offset_x=0.0, odom_offset_y=0.0,
            speed=0.18, goal_tolerance=0.15, start_delay=2.0, max_duration=60.0,
            human_release_delay=0.0, robot_start_delay=0.0,
            mode="independent", model_file=os.path.join(HOME, "ask_or_act", "predictor", "intent_model.pkl"),
            model_name="mlp", calibration="isotonic_dw", calib_condition="noisy",
            p_low=0.03, p_high=0.7, engage_dist=1.0, ask_dist=0.6, smooth_n=5, yield_timeout=8.0,
            clear_dist=0.6, caution_dist=1.5, answer_timeout=5.0,
            obs_noise=0.03, noise_seed="", true_intent="", result_file="", decisions_file="")
        for k, v in defaults.items():
            self.declare_parameter(k, v)
        p = lambda n: self.get_parameter(n).value
        sys.path.insert(0, p("aoa_dir"))
        sys.path.insert(0, p("fleet_dir"))
        from policy import AskOrActPolicy, load_predictor        # Ask or Act repository
        from fleet_qubo.fleet_sim import make_policy_class        # this repository
        FleetPolicy = make_policy_class(AskOrActPolicy)

        self.index, self.mode = p("robot_index"), p("mode")
        self.start, self.goal = (p("start_x"), p("start_y")), (p("goal_x"), p("goal_y"))
        self.offset = (p("odom_offset_x"), p("odom_offset_y"))
        self.speed, self.tol = p("speed"), p("goal_tolerance")
        self.start_delay, self.max_duration = p("start_delay"), p("max_duration")
        self.release_delay, self.robot_delay = p("human_release_delay"), p("robot_start_delay")
        self.result_file, self.decisions_file = p("result_file"), p("decisions_file")
        self.obs_noise = p("obs_noise")
        self.rng = random.Random(f"obs-{p('noise_seed')}")
        model, cal = load_predictor(p("model_file"), p("model_name"), p("calibration"), p("calib_condition"))
        self.pol = FleetPolicy(model, cal, mode=self.mode, p_low=p("p_low"), p_high=p("p_high"),
                               engage_dist=p("engage_dist"), ask_dist=p("ask_dist"), clear_dist=p("clear_dist"),
                               caution_dist=p("caution_dist"), answer_timeout=p("answer_timeout"),
                               true_intent=p("true_intent"), smooth_n=p("smooth_n"),
                               yield_timeout=p("yield_timeout"))

        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.release_pub = self.create_publisher(PoseStamped, "hunav_goal_pose", 10)
        self.ask_pub = self.create_publisher(String, "/fleet/ask", 10)
        self.request_pub = self.create_publisher(String, "/fleet/request", 10)
        self.status_pub = self.create_publisher(String, "/fleet/status", 10)
        self.create_subscription(Odometry, "odom", self.on_odom, 10)
        self.create_subscription(Agents, "human_states", self.on_humans, 10)
        self.create_subscription(String, "operator_answer", self.on_answer, 10)
        self.create_subscription(String, "assignment", self.on_assignment, 10)
        self.create_subscription(String, "/fleet/go", self.on_go, 10)

        self.pose, self.state, self.done = None, "WAIT_ODOM", False
        self.t_go = self.t_start = None
        self.released, self.request_sent = False, False
        self.humans, self.last_obs_t, self.last_step_t = {}, None, None
        self.stopped_time, self.min_dist = 0.0, float("inf")
        self.create_timer(0.05, self.step)
        self.create_timer(0.5, self.announce)
        self.get_logger().info(f"Robot {self.index}: mode {self.mode}, scenario {p('scenario_id')}")

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def status(self, state):
        self.status_pub.publish(String(data=json.dumps(dict(robot=self.index, state=state))))

    def announce(self):
        if self.state == "READY":
            self.status("ready")

    # ------------------------------------------------------------------ inputs
    def on_odom(self, msg):
        pos = msg.pose.pose.position
        self.pose = (pos.x + self.offset[0], pos.y + self.offset[1], yaw_from_quat(msg.pose.pose.orientation))

    def on_go(self, _msg):
        if self.t_go is None and self.state == "READY":
            self.t_go, self.state = self.now(), "DELAY"

    def on_answer(self, msg):
        a = json.loads(msg.data)
        t = self.now() - self.t_start if self.t_start is not None else 0.0
        self.pol.receive_answer(a["id"], a["intent"], t)

    def on_assignment(self, msg):
        a = json.loads(msg.data)
        self.pol.assigned[a["human"]] = int(a["action"])

    def on_humans(self, msg):
        for a in msg.agents:
            self.humans[a.id] = (a.position.position.x, a.position.position.y)
        if self.state == "DRIVING" and self.pose is not None:
            for hx, hy in self.humans.values():
                self.min_dist = min(self.min_dist, math.hypot(hx - self.pose[0], hy - self.pose[1]))

    def observe(self, t_abs):
        if self.last_obs_t is not None and t_abs - self.last_obs_t < 1.0 / OBS_RATE - 1e-6:
            return
        self.last_obs_t = t_abs
        for hid, (x, y) in self.humans.items():
            self.pol.add_observation(hid, t_abs, x + self.rng.gauss(0.0, self.obs_noise),
                                     y + self.rng.gauss(0.0, self.obs_noise))

    # ------------------------------------------------------------------ output
    def stop(self):
        self.cmd_pub.publish(Twist())

    def finish(self, outcome, elapsed):
        self.stop()
        self.state = "DONE"
        self.status("done")
        md = None if self.min_dist == float("inf") else round(self.min_dist, 3)
        whys = [d[4] for d in self.pol.decisions]
        res = dict(robot=self.index, outcome=outcome, duration=round(elapsed, 3), min_dist=md,
                   n_asks=len(self.pol.asks), asks=self.pol.asks, answers=self.pol.answers,
                   stopped_time=round(self.stopped_time, 3), mode=self.mode,
                   assigned={str(k): v for k, v in self.pol.assigned.items()},
                   held_s=round(self.pol.held_steps * 0.05, 3),
                   fallback=any("no answer" in w for w in whys),
                   robot_start_delay=self.robot_delay)
        if self.result_file:
            json.dump(res, open(self.result_file, "w"), indent=2)
        if self.decisions_file:
            with open(self.decisions_file, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["t", "human_id", "p_crossing", "action", "reason", "ahead_m", "dist_to_line_m"])
                w.writerows(self.pol.decisions)
        self.get_logger().info(f"Robot {self.index} finished ({outcome}), min distance {md}, "
                               f"asks {len(self.pol.asks)}")
        self.done = True

    # -------------------------------------------------------------------- loop
    def step(self):
        if self.pose is None or self.state in ("DONE", "ABORTED"):
            if self.state == "DONE":
                self.stop()
            return
        t_abs = self.now()
        # observe only from 2 s before this robot's own start, as the offline simulator does
        # (START_DELAY = 2 s), so waiting for the other robots adds no extra history
        observing = self.state == "DRIVING" or (
            self.state == "DELAY" and t_abs >= self.t_go + self.start_delay - 2.0)
        if self.humans and observing:
            self.observe(t_abs)
        if self.state == "WAIT_ODOM":
            off = math.hypot(self.pose[0] - self.start[0], self.pose[1] - self.start[1])
            if off > 0.3:
                self.get_logger().error(f"Robot {self.index} is {off:.2f} m from its start point.")
                self.state, self.done = "ABORTED", True
                self.status("aborted")
                return
            self.state = "READY"
            return
        if self.state in ("READY",):
            return
        if self.state == "DELAY":
            if t_abs - self.t_go >= self.start_delay:
                self.t_start, self.state = t_abs, "DRIVING"
            return

        x, y, yaw = self.pose
        dx, dy = self.goal[0] - x, self.goal[1] - y
        elapsed = t_abs - self.t_start
        dt = 0.0 if self.last_step_t is None else t_abs - self.last_step_t
        self.last_step_t = t_abs
        if not self.released and elapsed >= self.release_delay:
            msg = PoseStamped()
            msg.header.frame_id = "map"
            msg.pose.orientation.w = 1.0
            self.release_pub.publish(msg)
            self.released = True
        if math.hypot(dx, dy) < self.tol:
            self.finish("reached goal", elapsed)
            return
        if elapsed > self.max_duration:
            self.finish("timed out", elapsed)
            return
        if elapsed < self.robot_delay or self.speed <= 0.0:
            self.stop()
            return
        go, _, to_ask = self.pol.decide(elapsed, x)
        if self.pol.request is not None and not self.request_sent:
            hid, p = self.pol.request
            self.request_pub.publish(String(data=json.dumps(dict(robot=self.index, human=hid, p=p))))
            self.request_sent = True
        for hid in to_ask:
            self.ask_pub.publish(String(data=json.dumps(dict(robot=self.index, human=int(hid)))))
        if not go:
            self.stopped_time += dt
            self.stop()
            return
        err = wrap(math.atan2(dy, dx) - yaw)
        cmd = Twist()
        cmd.angular.z = max(-1.0, min(1.0, 1.5 * err))
        cmd.linear.x = 0.0 if abs(err) > 0.5 else self.speed
        self.cmd_pub.publish(cmd)


def main():
    rclpy.init()
    node = FleetController()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.stop()
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()
