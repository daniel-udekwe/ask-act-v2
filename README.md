# fleet_qubo

Joint go / stop / ask allocation for a robot fleet, written as a QUBO and solved with
QAOA (Qiskit) against exact and heuristic classical solvers. Companion code to the
research proposal *Joint Ask/Yield Allocation for Robot Fleets with QAOA*.

## Install

```
pip install qiskit==2.6.1 qiskit-aer==0.18.2 ortools==9.15.6755 numpy scipy pandas pytest
```

## Layout

| Path | Contents |
| --- | --- |
| `fleet_qubo/instances.py` | Problem definition, per-robot costs, corridor layouts, synthetic probabilities |
| `fleet_qubo/qubo.py` | QUBO builder with slack and unbalanced-penalization budget encodings; decoding |
| `fleet_qubo/classical.py` | Exhaustive search, OR-Tools CP-SAT, simulated annealing, greedy, independent Ask or Act rule |
| `fleet_qubo/qaoa.py` | Exact numpy QAOA simulator, INTERP depth growth, CVaR objective, metrics, Qiskit circuit export |
| `tests/test_core.py` | Checks every component against brute force (84 tests) |
| `scripts/tune_unbalanced.py` | Tunes unbalanced-penalization weights on seeds 1000-1049 |
| `scripts/pilot.py` | Month-1 noiseless pilot on development seeds 3000-3009 |
| `scripts/summarise_pilot.py` | Tables and figure from the pilot |

## Model

Variables per robot: `a_i` (ask), `s_i` (stop); go when both are 0. Expected costs:

- go: `C * p_i`
- stop: `tau_s * (1 - p_i)` (unnecessary stop)
- ask: `tau_a + kappa + C * p_i * (1 - alpha)`

Defaults `C = 10, tau_s = 10, tau_a = 1.5, kappa = 0.5, alpha = 1` make the uncoupled
optimum the Ask or Act band (go below 0.2, stop above 0.8, ask in between).
Couplings: congestion `w_ij * h_i * h_j` (both halted), conflict `v_ij * g_i * g_j` (both go).
Budget: at most `B = ceil(N/3)` questions per epoch.

Qubit `k` is variable `k` in Qiskit's little-endian order: `a_0..a_{N-1}, s_0..s_{N-1}`, then slack bits.

## Seed blocks

| Seeds | Use |
| --- | --- |
| 1000-1049 | Penalty tuning |
| 3000-3009 | Development pilot (synthetic instances) |
| 4000-4099 | Development pool of Ask or Act scenarios (per condition block) |
| 4000000+, 4100000+ | Development epoch draws (epoch evaluation, noisy QAOA) |
| 8000-8099 | Reserved fleet final pool; do not use before the freeze |

## Real probabilities (month 2)

`fleet_qubo/pool.py` builds epochs from Ask or Act scenarios. Probabilities come from
`scripts/extract_deadline_probs.py`, which runs the unchanged Ask or Act offline simulator
with the band disabled and records each scenario's smoothed calibrated probability at the
0.6 m deadline, for raw, conventional isotonic and decision-aware isotonic calibration.

To regenerate (needs the public repo `daniel-udekwe/turtlebot3-ask_or_act`):

```
python build_dataset.py --out ~/aoa_data/predictor          # in the Ask or Act repo
python train_predictor.py --dir ~/aoa_data/predictor
python scripts/extract_deadline_probs.py --aoa <repo> --model ~/aoa_data/predictor/intent_model.pkl
```

The predictor was retrained with scikit-learn 1.9 rather than 0.23.2, so probabilities differ
slightly from the paper's model; decision-window ECE under noise is 0.060 (conventional) and
0.014 (decision-aware), against 0.056 and 0.017 in the paper.

## Placeholders to replace

- Cost weights. With `C = tau_s = 10` a collision costs the same as an unnecessary stop, so a
  robot denied a question goes whenever p < 0.5. See `results/cost_ratio_sweep.md`; the ratio
  must be fixed before the freeze.
- Corridor weights `w = 2`, `v = 3` are placeholders until derived from corridor geometry.
- `synthetic_probs` is kept only for scaling studies.

## Run

```
python -m pytest -q
python scripts/tune_unbalanced.py
python scripts/pilot.py
python scripts/summarise_pilot.py
```
