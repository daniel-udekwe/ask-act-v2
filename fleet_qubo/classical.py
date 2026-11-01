"""Classical solvers and baselines."""
from __future__ import annotations

import time

import numpy as np

from .instances import Instance, GO, STOP, ASK, true_cost, feasible
from .qubo import Qubo, decode_index


# --------------------------------------------------------------------------- #
# Exhaustive search over the 3^N action space (ground truth)
# --------------------------------------------------------------------------- #
def action_table(inst: Instance):
    """Cost and feasibility of every action vector, indexed by base-3 key
    (digit i = action of robot i). Returns (costs, feasible_mask)."""
    N = inst.N
    keys = np.arange(3 ** N, dtype=np.int64)
    acts = np.stack([(keys // 3 ** i) % 3 for i in range(N)], axis=1)
    U = inst.unary_costs()
    costs = U[np.arange(N)[None, :], acts].sum(axis=1)
    halted = acts != GO
    goes = acts == GO
    for (i, j), w in inst.Ec.items():
        costs += w * (halted[:, i] & halted[:, j])
    for (i, j), v in inst.En.items():
        costs += v * (goes[:, i] & goes[:, j])
    n_ask = (acts == ASK).sum(axis=1)
    costs += inst.q * n_ask * (n_ask - 1) / 2
    feas = (acts == ASK).sum(axis=1) <= inst.B
    return costs, feas


def exhaustive(inst: Instance):
    t0 = time.perf_counter()
    costs, feas = action_table(inst)
    c = np.where(feas, costs, np.inf)
    k = int(np.argmin(c))
    acts = np.array([(k // 3 ** i) % 3 for i in range(inst.N)])
    return {"actions": acts, "cost": float(c[k]), "time": time.perf_counter() - t0}


# --------------------------------------------------------------------------- #
# Exact solver: OR-Tools CP-SAT on the original constrained problem
# --------------------------------------------------------------------------- #
def cpsat(inst: Instance, scale: int = 10_000, time_limit: float = 10.0):
    from ortools.sat.python import cp_model

    if inst.q:
        raise NotImplementedError("cpsat does not model the queue term; use exhaustive")
    t0 = time.perf_counter()
    N = inst.N
    m = cp_model.CpModel()
    x = [[m.new_bool_var(f"x{i}_{k}") for k in range(3)] for i in range(N)]
    for i in range(N):
        m.add_exactly_one(x[i])
    m.add(sum(x[i][ASK] for i in range(N)) <= inst.B)
    U = np.rint(inst.unary_costs() * scale).astype(int)
    obj = [int(U[i, k]) * x[i][k] for i in range(N) for k in range(3)]
    for (i, j), w in inst.Ec.items():           # both halted = (1-go_i)(1-go_j)
        y = m.new_bool_var(f"c{i}_{j}")
        m.add_bool_or([x[i][GO], x[j][GO], y])  # y >= 1 - go_i - go_j
        obj.append(int(round(w * scale)) * y)
    for (i, j), v in inst.En.items():           # both go
        y = m.new_bool_var(f"n{i}_{j}")
        m.add_bool_or([x[i][GO].Not(), x[j][GO].Not(), y])
        obj.append(int(round(v * scale)) * y)
    m.minimize(sum(obj))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 1
    status = solver.solve(m)
    acts = np.array([next(k for k in range(3) if solver.value(x[i][k])) for i in range(N)])
    return {"actions": acts, "cost": true_cost(inst, acts),
            "optimal": status == cp_model.OPTIMAL, "time": time.perf_counter() - t0}


# --------------------------------------------------------------------------- #
# Simulated annealing on the QUBO (same objective QAOA sees)
# --------------------------------------------------------------------------- #
def simulated_annealing(qubo: Qubo, inst: Instance, sweeps: int = 1000, restarts: int = 32,
                        T0: float | None = None, T1: float = 0.05, seed: int = 0):
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    n = qubo.n
    Q = np.zeros((n, n))
    for (i, j), c in qubo.quad.items():
        Q[i, j] = Q[j, i] = c
    lin = qubo.lin
    if T0 is None:
        T0 = qubo.max_abs_coeff()
    best_x, best_e = None, np.inf
    temps = np.geomspace(T0, T1, sweeps)
    for _ in range(restarts):
        x = rng.integers(0, 2, n).astype(float)
        field_ = lin + Q @ x
        e = qubo.energy(x)
        for T in temps:
            for k in rng.permutation(n):
                d = (1 - 2 * x[k]) * field_[k]       # energy change of flipping k
                if d <= 0 or rng.random() < np.exp(-d / T):
                    step = 1 - 2 * x[k]
                    x[k] += step
                    field_ += step * Q[:, k]
                    e += d
        if e < best_e:
            best_e, best_x = e, x.copy()
    idx = int(sum(int(b) << k for k, b in enumerate(best_x)))
    acts = decode_index(idx, inst.N)
    ok = (acts >= 0).all() and feasible(inst, acts)
    return {"actions": acts, "cost": true_cost(inst, acts) if ok else np.inf,
            "feasible": bool(ok), "time": time.perf_counter() - t0}


# --------------------------------------------------------------------------- #
# Heuristic baselines
# --------------------------------------------------------------------------- #
def independent_rule(inst: Instance, lo: float = 0.2, hi: float = 0.8, seed: int = 0):
    """Ask or Act band per robot, no coordination. Questions beyond the budget are
    refused in random order (first-come-first-served) and those robots stop."""
    rng = np.random.default_rng(seed)
    p = np.asarray(inst.p)
    acts = np.where(p >= hi, STOP, np.where(p <= lo, GO, ASK))
    askers = np.flatnonzero(acts == ASK)
    if len(askers) > inst.B:
        refused = rng.permutation(askers)[inst.B:]
        acts[refused] = STOP
    return {"actions": acts, "cost": true_cost(inst, acts)}


def greedy_budget(inst: Instance):
    """Per-robot cost minimiser; if the budget binds, keep the questions with the
    largest saving over each robot's best non-asking action. Ignores coupling."""
    U = inst.unary_costs()
    acts = U.argmin(axis=1)
    askers = np.flatnonzero(acts == ASK)
    if len(askers) > inst.B:
        alt = np.where(U[:, GO] <= U[:, STOP], GO, STOP)
        saving = U[askers, alt[askers]] - U[askers, ASK]
        drop = askers[np.argsort(saving)][: len(askers) - inst.B]
        acts[drop] = alt[drop]
    return {"actions": acts, "cost": true_cost(inst, acts)}
