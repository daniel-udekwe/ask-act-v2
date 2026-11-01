# Month 5: QAOA variants, transpilation, and the hardware pre-registration

Development seeds only. Decisions taken on 1 Nov and now in the proposal: H1 is restated as delay
superiority with collision non-inferiority (0.5 percentage points) at a matched question rate; the
primary operator cost is κ = 1.5 (a question occupies the operator for 1.5 s, and an
operator-second is valued like a robot-second). With τₐ = 1.5 each robot's own optimum now goes
below p = 0.03, stops above p = 0.7 and asks in between.

## 1. QAOA variants (`scripts/qaoa_variants.py`, `results/qaoa_variants_summary.md`)

Queue formulation, κ = 1.5, six real-probability instances per size (two at N = 10), noiseless.
All variants use INTERP depth growth and the same restart budget (3; 1 at N = 10).

- **Vanilla**: standard QAOA.
- **Warm start** (Egger et al. 2021): starts from each robot's own optimum, ignoring the queue,
  softened to c = 0.25 / 0.75. A new mixer and simulator path, tested against Qiskit's circuit.
- **CVaR** (α = 0.1): optimises the best 10% of the output distribution.

Depth 3, means over instances:

| N | Qubits | Variant | Feasible | Optimum probability | Lift (median) | Feasible cost above optimum (median) | Samples cheaper than the per-robot heuristic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 8 | Vanilla | 99.7% | 0.074 | 16× | 20% | 52% |
| 4 | 8 | Warm | 99.4% | 0.093 | 18× | 21% | 60% |
| 4 | 8 | CVaR | 92.6% | 0.075 | 16× | 29% | 53% |
| 6 | 12 | Vanilla | 99.6% | 0.013 | 63× | 23% | 87% |
| 6 | 12 | Warm | 99.1% | 0.014 | 67× | 32% | 78% |
| 6 | 12 | CVaR | 98.7% | 0.014 | 64× | 24% | 85% |
| 8 | 16 | Vanilla | 99.4% | 0.0037 | 251× | 20% | 98% |
| 8 | 16 | Warm | 98.6% | 0.0039 | 233× | 25% | 94% |
| 8 | 16 | CVaR | 97.7% | 0.0036 | 255× | 22% | 96% |

At N = 10 (20 qubits, two instances, one restart each), depth 3:

| N | Qubits | Variant | Feasible | Optimum probability | Lift (median) | Feasible cost above optimum (median) | Samples cheaper than the per-robot heuristic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 20 | Vanilla | 93.7% | 0.0005 | 511× | 89% | 68% |
| 10 | 20 | Warm | 95.3% | 0.0000 | 0.2× | 123% | 48% |
| 10 | 20 | CVaR | 84.7% | 0.0006 | 607× | 62% | 74% |

At N = 10 depth 3 is not enough: the feasible expected cost is 60-90% above the optimum, against
about 20% at N = 4-8. CVaR does best here, but this rests on two instances and a single restart.

- **Vanilla wins on simplicity at no cost up to N = 8.** It has the highest feasibility there and
  the lowest feasible expected cost in about half the instances. Neither alternative beats it
  consistently. At N = 10 CVaR is ahead on two instances, which is worth a closer look but is not
  enough to change the hardware choice: hardware runs stop at N = 6.
- **Warm start helps only when its start is good.** At N = 4 the per-robot heuristic is 20%
  above the optimum and warm start edges ahead. By N = 8-10 the heuristic is 73-129% above the
  optimum. Warm start's depth-1 circuit then sits near that poor start (lift below 1 at N = 8 and
  10) and needs depth 2 to recover.
- **CVaR mostly ties with vanilla**, at a small feasibility cost. Its objective is flat over much
  of parameter space, so the optimiser often stops early.
- **QAOA beats the obvious classical heuristic.** At N = 8 depth 3, 98% of vanilla's samples are
  cheaper than every robot choosing for itself. That heuristic is what a fleet without
  coordination would do, so this is the clearest positive statement QAOA earns here.

## 2. Transpilation (`scripts/transpile_tuning.py`, `results/transpile_tuning.csv`)

CZ gates after compiling queue circuits for `ibm_kingston`:

| N | Depth | Level 1 | Level 3 | Level 3, best of 20 seeds | Line swap strategy |
| --- | --- | --- | --- | --- | --- |
| 4 | 1 | 35 | 27 | 27 | 55 |
| 4 | 2 | 64 | 60 | 58 | 101 |
| 6 | 1 | 84 | 77 | 63 | 147 |
| 6 | 2 | 204 | 157 | 149 | 268 |
| 8 | 1 | 183 | 133 | 126 | 230 |
| 8 | 2 | 405 | 327 | 314 | 492 |

Best of 20 seeds saves up to 18% for under 2 s of compile time. Qiskit's commuting-gate routing
with a line swap strategy is built for fully connected cost graphs. It is worse here because the
queue term couples only the ask qubits (plus each robot's ask-stop pair), so many of the SWAP
layers do nothing useful.

## 3. Hardware pre-registration (`prereg/HARDWARE.md`, `prereg/hardware.json`)

- **What runs:** 40 circuits on `ibm_kingston`: N = 4 and 6, 10 final-pool instances each,
  depths 1 and 2, vanilla QAOA, 4,000 shots, level 3 best of 20 seeds, one Batch.
- **Budget:** about 2-3 minutes of QPU time, within the free 10 minutes per 28 days.
- **What is reported:** descriptive comparisons with the noiseless and noise-model predictions
  for the same circuits; no confirmatory test.
- **Runner:** `scripts/hardware_run.py`. It refuses to touch hardware without `--confirm-frozen`
  and the final pool, and its dry run on the noise model works.

To run it you need an IBM Quantum account saved on the machine (see the script's docstring).

## What is left before the freeze (month 6 plan)

1. Write the frozen analysis plan: H1-H3, metrics, the matched-rate procedure for H1, the
   non-inferiority margin, seeds, and this hardware protocol. Tag the code.
2. Build the final scenario pool (seeds 8000-8099) only after tagging.
3. Final runs: closed loop (H1, H3), QAOA benchmark (H2), hardware.
4. Gazebo validation with 3-4 TurtleBot3s (needs your machine with ROS 2).
