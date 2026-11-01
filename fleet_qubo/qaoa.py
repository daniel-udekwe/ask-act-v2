"""QAOA on the fleet QUBO.

Two equivalent back ends:
  * a fast exact statevector simulator in numpy (diagonal cost layer, RX mixer)
    used for parameter optimisation and the pilot sweeps;
  * the Qiskit circuit (QAOAAnsatz + Statevector / Aer) used to check equivalence
    and, later, to run with noise models and on IBM hardware.
"""
from __future__ import annotations

import time

import numpy as np
from scipy.optimize import minimize

from .instances import Instance
from .qubo import Qubo, decode_all
from .classical import action_table


# --------------------------------------------------------------------------- #
# Problem data on the full basis
# --------------------------------------------------------------------------- #
class QaoaProblem:
    def __init__(self, qubo: Qubo, inst: Instance):
        self.qubo, self.inst, self.n = qubo, inst, qubo.n
        E = qubo.energies_all()
        self.shift = float(E.mean())
        self.scale = float(E.std()) or 1.0
        self.h = (E - self.shift) / self.scale          # normalised cost diagonal
        self.order = np.argsort(self.h)
        self.E = E
        key, valid = decode_all(inst.N, qubo.n)
        costs, feas = action_table(inst)
        self.state_cost = np.where(valid, costs[key], np.inf)
        self.state_feas = valid & feas[key]
        self.opt_cost = float(np.min(np.where(feas, costs, np.inf)))
        self.state_opt = self.state_feas & np.isclose(self.state_cost, self.opt_cost)
        # does the QUBO ground state encode a true optimum?
        gs = np.flatnonzero(np.isclose(E, E.min()))
        self.ground_state_ok = bool(self.state_opt[gs].all())


# --------------------------------------------------------------------------- #
# numpy statevector simulation
# --------------------------------------------------------------------------- #
def _apply_1q(psi: np.ndarray, M: np.ndarray, k: int, n: int) -> None:
    """Apply the 2x2 matrix M to qubit k (bit k of the basis index) in place."""
    v = psi.reshape(1 << (n - 1 - k), 2, 1 << k)
    a0 = v[:, 0, :].copy()
    a1 = v[:, 1, :].copy()
    v[:, 0, :] = M[0, 0] * a0 + M[0, 1] * a1
    v[:, 1, :] = M[1, 0] * a0 + M[1, 1] * a1


def _ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def warm_angles(c: np.ndarray) -> np.ndarray:
    """Warm-start angles theta_i = 2 arcsin(sqrt(c_i)) (Egger et al. 2021)."""
    return 2 * np.arcsin(np.sqrt(np.clip(c, 0.0, 1.0)))


def warm_from_bits(bits, eps: float = 0.25) -> np.ndarray:
    """Regularised warm start from a classical bitstring: c_i = eps or 1 - eps."""
    bits = np.asarray(bits, dtype=float)
    return np.where(bits > 0.5, 1.0 - eps, eps)


def _mixers(beta: float, n: int, warm):
    """Per-qubit mixer matrices. Standard: exp(-i beta X). Warm start:
    Ry(theta) exp(-i beta Z) Ry(-theta), which equals exp(-i beta X) at c = 0.5."""
    if warm is None:
        c, s = np.cos(beta), -1j * np.sin(beta)
        M = np.array([[c, s], [s, c]], dtype=complex)
        return [M] * n
    D = np.diag([np.exp(-1j * beta), np.exp(1j * beta)])
    return [_ry(t) @ D @ _ry(-t) for t in warm_angles(warm)]


def initial_state(n: int, warm=None) -> np.ndarray:
    if warm is None:
        return np.full(1 << n, 1 / np.sqrt(1 << n), dtype=complex)
    psi = np.array([1.0 + 0j])
    for t in warm_angles(warm)[::-1]:          # kron(q_{n-1}, ..., q_0): bit k <-> qubit k
        psi = np.kron(psi, np.array([np.cos(t / 2), np.sin(t / 2)]))
    return psi


def qaoa_state(params: np.ndarray, prob: QaoaProblem, warm: np.ndarray | None = None):
    """warm: None for standard QAOA, or a length-n vector c_i in [0, 1] (warm start)."""
    p = len(params) // 2
    gammas, betas = params[:p], params[p:]
    n = prob.n
    psi = initial_state(n, warm)
    for g, b in zip(gammas, betas):
        psi = psi * np.exp(-1j * g * prob.h)
        for k, M in enumerate(_mixers(b, n, warm)):
            _apply_1q(psi, M, k, n)
    return psi


def objective(params, prob: QaoaProblem, cvar: float | None = None, warm=None):
    probs = np.abs(qaoa_state(params, prob, warm)) ** 2
    if cvar is None:
        return float(probs @ prob.h)
    # CVaR_alpha: mean energy of the lowest-energy alpha fraction of the distribution
    order = prob.order
    ps = probs[order]
    before = np.concatenate([[0.0], np.cumsum(ps)[:-1]])
    w = np.minimum(ps, np.clip(cvar - before, 0.0, None))
    return float(w @ prob.h[order] / cvar)


def interp(params: np.ndarray) -> np.ndarray:
    """INTERP initialisation (Zhou et al. 2020): depth p -> p + 1."""
    p = len(params) // 2
    out = []
    for vec in (params[:p], params[p:]):
        v = np.concatenate([[0.0], vec, [0.0]])
        out.append(np.array([(i / p) * v[i] + ((p - i) / p) * v[i + 1]
                             for i in range(p + 1)]))
    return np.concatenate(out)


def optimise(prob: QaoaProblem, depth: int, init: np.ndarray | None = None,
             cvar: float | None = None, restarts: int = 4, seed: int = 0, maxiter: int = 400,
             warm: np.ndarray | None = None):
    rng = np.random.default_rng(seed)
    starts = [] if init is None else [init]
    while len(starts) < restarts:
        starts.append(np.concatenate([rng.uniform(0, 0.8, depth), rng.uniform(0, 0.8, depth)]))
    best = None
    for x0 in starts:
        res = minimize(objective, x0, args=(prob, cvar, warm), method="COBYLA",
                       options={"maxiter": maxiter, "rhobeg": 0.2})
        if best is None or res.fun < best.fun:
            best = res
    return best.x, float(best.fun)


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def evaluate(params, prob: QaoaProblem, shots: int = 1024, seed: int = 0, warm=None) -> dict:
    probs = np.abs(qaoa_state(params, prob, warm)) ** 2
    probs /= probs.sum()
    rng = np.random.default_rng(seed)
    samples = rng.choice(len(probs), size=shots, p=probs)
    feas = prob.state_feas[samples]
    best = float(prob.state_cost[samples][feas].min()) if feas.any() else np.inf
    opt = prob.opt_cost
    gap = (best - opt) / abs(opt) if np.isfinite(best) else np.inf
    # same-shot baseline: uniform random bitstrings (what QAOA must beat)
    rnd = rng.integers(0, len(probs), size=shots)
    rfeas = prob.state_feas[rnd]
    rbest = float(prob.state_cost[rnd][rfeas].min()) if rfeas.any() else np.inf
    rgap = (rbest - opt) / abs(opt) if np.isfinite(rbest) else np.inf
    p_feas = float(probs[prob.state_feas].sum())
    exp_cost = (float(probs[prob.state_feas] @ prob.state_cost[prob.state_feas]) / p_feas
                if p_feas > 0 else np.inf)
    return {
        "p_opt": float(probs[prob.state_opt].sum()),
        "p_feasible": p_feas,
        "best_sample_gap": gap,
        "within_5pct": bool(gap <= 0.05),
        "found_opt": bool(gap <= 1e-9),
        "expected_feasible_cost": exp_cost,
        "random_p_opt": float(prob.state_opt.mean()),
        "random_p_feasible": float(prob.state_feas.mean()),
        "random_best_gap": rgap,
        "random_found_opt": bool(rgap <= 1e-9),
    }


def run_qaoa(qubo: Qubo, inst: Instance, depths=(1, 2, 3), cvar=None, seed=0, restarts=4):
    t0 = time.perf_counter()
    prob = QaoaProblem(qubo, inst)
    results, params = [], None
    for d in depths:
        init = interp(params) if params is not None else None
        params, fval = optimise(prob, d, init=init, cvar=cvar, restarts=restarts, seed=seed)
        m = evaluate(params, prob, seed=seed)
        m.update(depth=d, objective=fval, params=params.tolist(),
                 ground_state_ok=prob.ground_state_ok, n_qubits=qubo.n,
                 time=time.perf_counter() - t0)
        results.append(m)
    return results


# --------------------------------------------------------------------------- #
# Qiskit circuit (for equivalence checks, noise models and hardware)
# --------------------------------------------------------------------------- #
def qiskit_cost_operator(prob: QaoaProblem):
    """Ising operator equal to the normalised diagonal (x_k = (1 - Z_k) / 2)."""
    from qiskit.quantum_info import SparsePauliOp

    q, sc = prob.qubo, prob.scale
    terms = []
    const = q.const
    for k, c in enumerate(q.lin):
        if c:
            const += c / 2
            terms.append(("Z", [k], -c / 2 / sc))
    for (i, j), c in q.quad.items():
        const += c / 4
        terms.append(("Z", [i], -c / 4 / sc))
        terms.append(("Z", [j], -c / 4 / sc))
        terms.append(("ZZ", [i, j], c / 4 / sc))
    terms.append(("I", [0], (const - prob.shift) / sc))
    return SparsePauliOp.from_sparse_list(terms, num_qubits=q.n).simplify()


def qiskit_circuit(prob: QaoaProblem, params: np.ndarray, measure: bool = False, warm=None):
    from qiskit.circuit.library import QAOAAnsatz
    if warm is not None:
        return _warm_circuit(prob, params, measure, warm)

    p = len(params) // 2
    ansatz = QAOAAnsatz(qiskit_cost_operator(prob), reps=p)
    gammas, betas = params[:p], params[p:]
    bind = {}
    for prm in ansatz.parameters:
        idx = int(prm.name.split("[")[1].rstrip("]"))
        bind[prm] = gammas[idx] if prm.name.startswith("γ") else betas[idx]
    qc = ansatz.assign_parameters(bind)
    if measure:
        qc.measure_all()
    return qc


def _warm_circuit(prob: QaoaProblem, params: np.ndarray, measure: bool, warm):
    """Warm-start QAOA: Ry(theta_i) initial state, mixer Ry(theta) Rz(2 beta) Ry(-theta)."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import PauliEvolutionGate

    n, p = prob.n, len(params) // 2
    th = warm_angles(warm)
    op = qiskit_cost_operator(prob)
    qc = QuantumCircuit(n)
    for k in range(n):
        qc.ry(th[k], k)
    for g, b in zip(params[:p], params[p:]):
        qc.append(PauliEvolutionGate(op, time=g), range(n))
        for k in range(n):
            qc.ry(-th[k], k)
            qc.rz(2 * b, k)
            qc.ry(th[k], k)
    if measure:
        qc.measure_all()
    return qc
