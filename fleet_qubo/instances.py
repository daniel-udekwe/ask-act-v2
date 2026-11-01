"""Problem instances for joint go / stop / ask allocation in a robot fleet.

Each robot i holds a calibrated crossing probability p_i for the pedestrian it
faces in the current decision epoch. Robots choose one of three actions:

    GO   (a_i = 0, s_i = 0)
    STOP (a_i = 0, s_i = 1)   yield to the pedestrian
    ASK  (a_i = 1, s_i = 0)   halt and ask; follow the answer

Per-robot expected cost (alpha = answer accuracy):

    go   : C * p_i
    stop : tau_s * (1 - p_i)                     unnecessary-stop cost
    ask  : tau_a + kappa + C * p_i * (1 - alpha)

With the defaults (C = 10, tau_s = 10, tau_a + kappa = 2) the uncoupled
optimum is exactly the Ask or Act band: go if p < 0.2, stop if p > 0.8,
ask otherwise.

Couplings:
    E_c (congestion): w_ij * h_i * h_j, with h_i = a_i + s_i (robot halted)
    E_n (conflict)  : v_ij * g_i * g_j, with g_i = 1 - a_i - s_i (robot goes)
Constraint: at most B questions per epoch (set B = N to drop it).
Queue (optional): q * a_i * a_j for every pair; with one operator answering serially,
each pair of askers adds one service time of waiting, so q = service time cost.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

GO, STOP, ASK = 0, 1, 2
ACTION_NAMES = {GO: "go", STOP: "stop", ASK: "ask"}


@dataclass
class Instance:
    p: np.ndarray                      # calibrated crossing probabilities, shape (N,)
    B: int                             # question budget per epoch
    C: float = 10.0                    # collision cost
    tau_s: float = 10.0                # cost of an unnecessary stop
    tau_a: float = 1.5                 # time cost of asking
    kappa: float = 0.5                 # operator cost per question
    alpha: float = 1.0                 # answer accuracy
    Ec: dict = field(default_factory=dict)   # (i, j) -> w_ij, congestion when both halt
    En: dict = field(default_factory=dict)   # (i, j) -> v_ij, conflict when both go
    q: float = 0.0                     # operator queue: cost per pair of robots that both ask
    name: str = ""

    @property
    def N(self) -> int:
        return len(self.p)

    def unary_costs(self) -> np.ndarray:
        """(N, 3) array of per-robot costs for GO, STOP, ASK."""
        p = np.asarray(self.p, dtype=float)
        go = self.C * p
        stop = self.tau_s * (1.0 - p)
        ask = self.tau_a + self.kappa + self.C * p * (1.0 - self.alpha)
        return np.stack([go, stop, ask], axis=1)


def true_cost(inst: Instance, actions) -> float:
    """Objective of an action vector (values in {GO, STOP, ASK}); ignores the budget."""
    actions = np.asarray(actions)
    U = inst.unary_costs()
    cost = float(U[np.arange(inst.N), actions].sum())
    halted = actions != GO
    goes = actions == GO
    for (i, j), w in inst.Ec.items():
        cost += w * halted[i] * halted[j]
    for (i, j), v in inst.En.items():
        cost += v * goes[i] * goes[j]
    n_ask = int(np.sum(actions == ASK))
    cost += inst.q * n_ask * (n_ask - 1) / 2
    return cost


def feasible(inst: Instance, actions) -> bool:
    return int(np.sum(np.asarray(actions) == ASK)) <= inst.B


def default_budget(N: int) -> int:
    return math.ceil(N / 3)


# --------------------------------------------------------------------------- #
# Synthetic probabilities (placeholder until Ask or Act pipeline outputs are wired in)
# --------------------------------------------------------------------------- #
def synthetic_probs(N: int, rng: np.random.Generator,
                    mix=(0.35, 0.30, 0.35)) -> np.ndarray:
    """Mixture resembling calibrated outputs at the deadline:
    confident not-crossing, ambiguous, confident crossing."""
    kind = rng.choice(3, size=N, p=mix)
    p = np.empty(N)
    p[kind == 0] = rng.beta(1.0, 9.0, size=(kind == 0).sum())
    p[kind == 1] = rng.uniform(0.2, 0.8, size=(kind == 1).sum())
    p[kind == 2] = rng.beta(9.0, 1.0, size=(kind == 2).sum())
    return p


# --------------------------------------------------------------------------- #
# Corridor graphs (stage 2). Weights scale with a single knob for robustness sweeps.
# --------------------------------------------------------------------------- #
def corridor_edges(N: int, layout: str, w: float = 2.0, v: float = 3.0):
    """Return (Ec, En) for a corridor layout.

    single   : robots in a line; adjacent robots congest when both halt.
    tjunction: a single corridor plus a narrow junction shared by the robots
               nearest the middle (conflict when both go).
    parallel : two corridors (even / odd robots) joined by one narrow section
               shared by the first robot of each corridor.
    """
    Ec, En = {}, {}
    if layout == "none":
        return Ec, En
    if layout == "single":
        for i in range(N - 1):
            Ec[(i, i + 1)] = w
    elif layout == "tjunction":
        for i in range(N - 1):
            Ec[(i, i + 1)] = w
        m = N // 2
        En[(m - 1, m)] = v
        if N >= 4:
            En[(m - 2, m)] = v
    elif layout == "parallel":
        left = list(range(0, N, 2))
        right = list(range(1, N, 2))
        for side in (left, right):
            for a, b in zip(side[:-1], side[1:]):
                Ec[(a, b)] = w
        En[(left[0], right[0])] = v
        if len(left) > 1 and len(right) > 1:
            En[(left[1], right[1])] = v
    else:
        raise ValueError(layout)
    return Ec, En


def make_instance(N: int, seed: int, layout: str = "none", B: int | None = None,
                  w: float = 2.0, v: float = 3.0, **cost_kwargs) -> Instance:
    rng = np.random.default_rng(seed)
    p = synthetic_probs(N, rng)
    Ec, En = corridor_edges(N, layout, w=w, v=v)
    return Instance(p=p, B=default_budget(N) if B is None else B, Ec=Ec, En=En,
                    name=f"N{N}_{layout}_s{seed}", **cost_kwargs)
