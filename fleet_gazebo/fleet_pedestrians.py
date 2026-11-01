#!/usr/bin/env python3
"""
One scripted pedestrian per fleet robot, in that robot's lane.

Same motion as Ask or Act's scripted_pedestrians.py (ped_traj.py trajectories, moved with
/set_entity_state in simulation time after the release signal), with three changes:
  * topics are relative, so the node runs in its robot's namespace;
  * the Gazebo model is shifted by `lane_offset_y`, while `human_states` reports the
    position in the Ask or Act frame (the robot's controller uses the same frame);
  * pedestrians do not answer questions; the shared operator does (fleet_coordinator.py).
"""
import json
import math
import os
import sys

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from gazebo_msgs.msg import EntityState
from gazebo_msgs.srv import SetEntityState, SpawnEntity
from hunav_msgs.msg import Agent, Agents

HOME = os.path.expanduser("~")


def quat(yaw):
    return 0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0)


class FleetPedestrian(Node):
    def __init__(self):
        super().__init__("fleet_pedestrian")
        for k, v in dict(aoa_dir=os.path.join(HOME, "ask_or_act"), labels_file="", scenario_id="",
                         lane_offset_y=0.0, model_name="pedestrian_0", rate=20.0).items():
            self.declare_parameter(k, v)
        p = lambda n: self.get_parameter(n).value
        sys.path.insert(0, p("aoa_dir"))
        from ped_traj import build_trajectory, pose_at
        from scripted_pedestrians import HUMAN_SDF
        self.pose_at, self.sdf = pose_at, HUMAN_SDF
        labels = {l["id"]: l for l in json.load(open(p("labels_file")))}
        lab = labels[p("scenario_id")]
        self.traj = build_trajectory(lab["start"], lab["plan"], lab["human_speed"])
        self.times = [s[0] for s in self.traj]
        self.dy, self.name = p("lane_offset_y"), p("model_name")
        self.spawn_cli = self.create_client(SpawnEntity, "/spawn_entity")
        self.set_cli = self.create_client(SetEntityState, "/set_entity_state")
        self.state_pub = self.create_publisher(Agents, "human_states", 10)
        self.create_subscription(PoseStamped, "hunav_goal_pose", self.on_release, 10)
        self.t_release, self.spawn_future, self.pending_set, self.ready = None, None, None, False
        self.create_timer(1.0 / p("rate"), self.step)

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_release(self, _msg):
        if self.t_release is None:
            self.t_release = self.now()

    def step(self):
        if not self.ready:
            if self.spawn_future is None and self.spawn_cli.service_is_ready():
                x, y, yaw, _ = self.pose_at(self.traj, self.times, 0.0)
                req = SpawnEntity.Request()
                req.name, req.xml = self.name, self.sdf
                req.initial_pose.position.x, req.initial_pose.position.y = x, y + self.dy
                (req.initial_pose.orientation.x, req.initial_pose.orientation.y,
                 req.initial_pose.orientation.z, req.initial_pose.orientation.w) = quat(yaw)
                self.spawn_future = self.spawn_cli.call_async(req)
            elif self.spawn_future is not None and self.spawn_future.done() and self.set_cli.service_is_ready():
                self.ready = True
            return
        t_rel = self.now() - self.t_release if self.t_release is not None else 0.0
        x, y, yaw, v = self.pose_at(self.traj, self.times, t_rel)
        qx, qy, qz, qw = quat(yaw)
        if self.pending_set is None or self.pending_set.done():
            req = SetEntityState.Request()
            req.state = EntityState(name=self.name, reference_frame="world")
            req.state.pose.position.x, req.state.pose.position.y = x, y + self.dy
            (req.state.pose.orientation.x, req.state.pose.orientation.y,
             req.state.pose.orientation.z, req.state.pose.orientation.w) = qx, qy, qz, qw
            self.pending_set = self.set_cli.call_async(req)
        agents = Agents()
        agents.header.stamp, agents.header.frame_id = self.get_clock().now().to_msg(), "odom"
        a = Agent()
        a.id = 1
        a.position.position.x, a.position.position.y = x, y            # Ask or Act frame
        (a.position.orientation.x, a.position.orientation.y,
         a.position.orientation.z, a.position.orientation.w) = qx, qy, qz, qw
        a.velocity.linear.x, a.velocity.linear.y = v * math.cos(yaw), v * math.sin(yaw)
        agents.agents.append(a)
        self.state_pub.publish(agents)


def main():
    rclpy.init()
    node = FleetPedestrian()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()
