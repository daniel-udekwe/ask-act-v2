import itertools

import numpy as np
import pytest

from fleet_qubo.instances import make_instance, true_cost, feasible, GO, STOP, ASK
from fleet_qubo.qubo import build_qubo, slack_coefficients, decode_index
from fleet_qubo.classical import exhaustive, cpsat, greedy_budget, simulated_annealing
from fleet_qubo.qaoa import QaoaProblem, qaoa_state, qiskit_circuit

LAYOUTS = ["none", "single", "tjunction", "parallel"]


@pytest.mark.parametrize("B", range(0, 8))
def test_slack_represents_exactly_0_to_B(B):
    c = slack_coefficients(B)
    sums = {sum(ci * b for ci, b in zip(c, bits))
            for bits in itertools.product([0, 1], repeat=len(c))}
    assert sums == set(range(B + 1))


@pytest.mark.parametrize("layout", LAYOUTS)
@pytest.mark.parametrize("seed", range(5))
def test_slack_qubo_energy_matches_cost(layout, seed):
    """For every feasible action vector, min over slack bits of the QUBO energy = true cost."""
    inst = make_instance(5, seed, layout)
    q = build_qubo(inst, "slack")
    E = q.energies_all()
    N = inst.N
    best = {}
    for idx, e in enumerate(E):
        acts = decode_index(idx, N)
        if (acts < 0).any():
            continue
        k = tuple(acts)
        best[k] = min(best.get(k, np.inf), e)
    for acts, e in best.items():
        if feasible(inst, acts):
            assert e == pytest.approx(true_cost(inst, acts), abs=1e-9)
        else:
            assert e > true_cost(inst, acts) + 1e-6


@pytest.mark.parametrize("layout", LAYOUTS)
@pytest.mark.parametrize("seed", range(5))
def test_slack_ground_state_is_true_optimum(layout, seed):
    inst = make_instance(6, seed, layout)
    prob = QaoaProblem(build_qubo(inst, "slack"), inst)
    assert prob.ground_state_ok


@pytest.mark.parametrize("layout", LAYOUTS)
@pytest.mark.parametrize("seed", range(5))
def test_cpsat_matches_exhaustive(layout, seed):
    inst = make_instance(7, seed, layout)
    assert cpsat(inst)["cost"] == pytest.approx(exhaustive(inst)["cost"], abs=1e-3)


@pytest.mark.parametrize("seed", range(10))
def test_greedy_optimal_without_coupling(seed):
    inst = make_instance(8, seed, "none")
    assert greedy_budget(inst)["cost"] == pytest.approx(exhaustive(inst)["cost"])


def test_uncoupled_optimum_is_ask_or_act_band():
    for p, want in [(0.05, GO), (0.19, GO), (0.5, ASK), (0.81, STOP), (0.95, STOP)]:
        inst = make_instance(1, 0, "none", B=1)
        inst.p = np.array([p])
        assert exhaustive(inst)["actions"][0] == want


@pytest.mark.parametrize("seed", range(3))
def test_simulated_annealing_finds_optimum_small(seed):
    # single-flip SA needs many restarts: ask <-> stop passes through a penalised state
    inst = make_instance(5, 3, "single")
    r = simulated_annealing(build_qubo(inst, "slack"), inst, seed=seed)
    assert r["cost"] == pytest.approx(exhaustive(inst)["cost"])


@pytest.mark.parametrize("encoding", ["slack", "unbalanced"])
def test_numpy_qaoa_matches_qiskit(encoding):
    from qiskit.quantum_info import Statevector

    inst = make_instance(3, 1, "single")
    prob = QaoaProblem(build_qubo(inst, encoding), inst)
    params = np.array([0.31, 0.72, 0.43, 0.17])
    ours = np.abs(qaoa_state(params, prob)) ** 2
    theirs = Statevector(qiskit_circuit(prob, params)).probabilities()
    assert np.allclose(ours, theirs, atol=1e-10)


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("layout", ["none", "single"])
def test_queue_qubo_needs_no_slack_and_matches_cost(seed, layout):
    inst = make_instance(5, seed, layout, B=5)
    inst.q = 1.5
    q = build_qubo(inst, "slack")
    assert q.n == 10                                   # 2N, no slack bits
    E = q.energies_all()
    for idx, e in enumerate(E):
        acts = decode_index(idx, inst.N)
        if (acts >= 0).all():
            assert e == pytest.approx(true_cost(inst, acts), abs=1e-9)
    prob = QaoaProblem(q, inst)
    assert prob.ground_state_ok


def test_warm_start_at_half_equals_standard():
    inst = make_instance(4, 2, "single")
    prob = QaoaProblem(build_qubo(inst, "slack"), inst)
    params = np.array([0.4, 0.9, 0.3, 0.6])
    std = qaoa_state(params, prob)
    warm = qaoa_state(params, prob, warm=np.full(prob.n, 0.5))
    assert np.allclose(std, warm, atol=1e-12)


def test_warm_start_numpy_matches_qiskit():
    from qiskit.quantum_info import Statevector
    from fleet_qubo.qaoa import warm_from_bits

    inst = make_instance(3, 4, "single")
    prob = QaoaProblem(build_qubo(inst, "slack"), inst)
    rng = np.random.default_rng(0)
    c = warm_from_bits(rng.integers(0, 2, prob.n), eps=0.25)
    params = np.array([0.31, 0.72, 0.43, 0.17])
    ours = np.abs(qaoa_state(params, prob, warm=c)) ** 2
    theirs = Statevector(qiskit_circuit(prob, params, warm=c)).probabilities()
    assert np.allclose(ours, theirs, atol=1e-10)
