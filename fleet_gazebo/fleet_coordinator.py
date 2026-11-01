#!/usr/bin/env python3
"""
Fleet coordinator: the shared operator and, in joint mode, the decision epochs.

  /fleet/status   (in)   {"robot", "state"}: ready / done / aborted
  /fleet/go       (out)  sent once every robot is ready; robots then start on their own delays
  /fleet/ask      (in)   {"robot", "human"}: a question for the operator
  /robot_<i>/operator_answer (out) {"id", "intent"} at the answer time
  /fleet/request  (in)   {"robot", "human", "p"}: a robot holding at its deadline (joint mode)
  /robot_<i>/assignment      (out) {"human", "action"} when the epoch closes

The rules live in coordinator_core.py, shared with the tests. The joint solver is the exact
solver on the queue formulation, as in the offline closed loop.
"""
import json
import os
import sys

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coordinator_core import Operator, Epochs   # noqa: E402

HOME = os.path.expanduser("~")


class FleetCoordinator(Node):
    def __init__(self):
        super().__init__("fleet_coordinator")
        for k, v in dict(fleet_dir=os.path.join(HOME, "fleet_qubo"), labels_file="", scenarios="",
                         mode="independent", service=1.5, answer_accuracy=1.0, window=1.5,
                         C=100.0, tau_s=10.0, tau_a=1.5, kappa=1.5, q=1.5, log_file="").items():
            self.declare_parameter(k, v)
        p = lambda n: self.get_parameter(n).value
        sys.path.insert(0, p("fleet_dir"))
        from fleet_qubo.instances import Instance
        from fleet_qubo.classical import exhaustive
        labels = {l["id"]: l for l in json.load(open(p("labels_file")))}
        self.scen = p("scenarios").split(",")
        self.truth = [labels[s]["intent"] for s in self.scen]
        self.n, self.mode, self.log_file = len(self.scen), p("mode"), p("log_file")
        cost = dict(C=p("C"), tau_s=p("tau_s"), tau_a=p("tau_a"), kappa=p("kappa"))
        q = p("q")

        def solve(ps, idx):
            inst = Instance(p=np.array(ps), B=len(ps), q=q, **cost)
            return exhaustive(inst)["actions"]

        self.operator = Operator(p("service"), p("answer_accuracy"))
        self.epochs = Epochs(self.n, solve, p("window"))
        self.ready, self.done, self.go_sent = set(), set(), False
        self.pending = []                                  # (answer time, robot, human, answer)
        self.answer_pub = [self.create_publisher(String, f"/robot_{i}/operator_answer", 10) for i in range(self.n)]
        self.assign_pub = [self.create_publisher(String, f"/robot_{i}/assignment", 10) for i in range(self.n)]
        self.go_pub = self.create_publisher(String, "/fleet/go", 10)
        self.humans = {}
        self.create_subscription(String, "/fleet/status", self.on_status, 10)
        self.create_subscription(String, "/fleet/ask", self.on_ask, 10)
        self.create_subscription(String, "/fleet/request", self.on_request, 10)
        self.create_timer(0.05, self.step)
        self.finished = False
        self.get_logger().info(f"Coordinator: {self.n} robots, mode {self.mode}")

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_status(self, msg):
        m = json.loads(msg.data)
        if m["state"] == "ready":
            self.ready.add(m["robot"])
        elif m["state"] in ("done", "aborted"):
            self.done.add(m["robot"])
            self.epochs.finish(m["robot"])

    def on_ask(self, msg):
        m = json.loads(msg.data)
        r = m["robot"]
        t_ans, ans = self.operator.ask(self.now(), r, self.scen[r], self.truth[r])
        self.pending.append((t_ans, r, m["human"], ans))

    def on_request(self, msg):
        m = json.loads(msg.data)
        self.humans[m["robot"]] = m["human"]
        self.epochs.request(self.now(), m["robot"], m["p"])

    def step(self):
        t = self.now()
        if not self.go_sent and len(self.ready) == self.n:
            self.go_pub.publish(String(data="go"))
            self.go_sent = True
        for item in [a for a in self.pending if a[0] <= t]:
            self.pending.remove(item)
            _, r, h, ans = item
            self.answer_pub[r].publish(String(data=json.dumps(dict(id=h, intent=ans))))
        if self.mode == "joint":
            for r, a in self.epochs.tick(t).items():
                self.assign_pub[r].publish(String(data=json.dumps(dict(human=self.humans[r], action=a))))
        if len(self.done) == self.n and not self.finished:
            self.finished = True
            if self.log_file:
                json.dump(dict(operator=self.operator.log, epochs=self.epochs.log),
                          open(self.log_file, "w"), indent=2, default=str)


def main():
    rclpy.init()
    node = FleetCoordinator()
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()
