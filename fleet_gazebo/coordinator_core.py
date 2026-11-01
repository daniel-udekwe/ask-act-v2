"""ROS-free core of the fleet coordinator: the shared operator and the decision epochs.

The rules are the ones in fleet_qubo/fleet_sim.py, so Gazebo and the offline simulator
make the same decisions from the same inputs:

  Operator  one operator answers questions first come, first served, `service` s each.
            A question asked at time t while the operator is busy until b is answered at
            max(t, b) + service. Answers use the scenario's own random stream
            (random.Random("answers-<scenario id>")), as in simulate_policies.simulate():
            one draw for whether it answers (always, response_prob = 1), one for accuracy.
  Epochs    a robot that reaches its deadline undecided sends a request (its smoothed
            probability) and holds. The epoch closes when no robot is still approaching
            (every robot has either requested or finished), or `window` s after the first
            waiting request. The joint solver then assigns go / stop / ask to every waiting robot.
"""
from __future__ import annotations

import random

GO, STOP, ASK = 0, 1, 2


class Operator:
    def __init__(self, service: float = 1.5, answer_accuracy: float = 1.0):
        self.service, self.accuracy = service, answer_accuracy
        self.busy_until = float("-inf")
        self.rngs = {}
        self.log = []

    def ask(self, t: float, robot: int, scenario_id: str, true_intent: str):
        """Return (answer time, answer) for a question asked at time t."""
        rng = self.rngs.setdefault(scenario_id, random.Random(f"answers-{scenario_id}"))
        rng.random()                                    # response_prob = 1: always answers
        wrong = "not_crossing" if true_intent == "crossing" else "crossing"
        answer = true_intent if rng.random() < self.accuracy else wrong
        start = max(t, self.busy_until)
        self.busy_until = start + self.service
        self.log.append(dict(robot=robot, asked=round(t, 3), answered=round(self.busy_until, 3), answer=answer))
        return self.busy_until, answer


class Epochs:
    def __init__(self, n_robots: int, solve, window: float = 1.5):
        """solve(list of p, list of robot indices) -> list of actions."""
        self.n, self.solve, self.window = n_robots, solve, window
        self.requests = {}          # robot -> p, waiting for an assignment
        self.assigned = {}          # robot -> action
        self.finished = set()
        self.opened = None
        self.log = []

    def request(self, t: float, robot: int, p: float):
        if robot in self.assigned or robot in self.requests:
            return
        self.requests[robot] = p
        if self.opened is None:
            self.opened = t

    def finish(self, robot: int):
        self.finished.add(robot)

    def tick(self, t: float):
        """Call once per control step after all inputs; returns {robot: action} when an epoch closes."""
        if self.opened is None:
            return {}
        approaching = [r for r in range(self.n)
                       if r not in self.requests and r not in self.assigned and r not in self.finished]
        if approaching and t - self.opened < self.window - 1e-9:
            return {}
        idx = sorted(self.requests)
        acts = self.solve([self.requests[r] for r in idx], idx)
        out = {r: int(a) for r, a in zip(idx, acts)}
        self.assigned.update(out)
        self.log.append(dict(t=round(t, 3), robots=idx, held_s=round(t - self.opened, 3), actions=out))
        self.requests, self.opened = {}, None
        return out
