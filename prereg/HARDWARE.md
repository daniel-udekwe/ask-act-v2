# Pre-registration: QAOA on IBM hardware

Status: draft, to be frozen with the rest of the analysis plan before any final run.
Machine-readable settings: `prereg/hardware.json`. Runner: `scripts/hardware_run.py`.

## What runs

| Setting | Value |
| --- | --- |
| Backend | `ibm_kingston` (Heron r2, IBM Open Plan) |
| Formulation | Queue (no budget), C = 100, τₛ = 10, τₐ = 1.5, κ = 1.5, q = 1.5 |
| Probabilities | Noisy tracking, decision-aware calibration, reserved final scenario pool (seeds 8000-8099) |
| Instances | N = 4 and N = 6, 10 each; epoch seeds 8 500 000 + k, k = 0-9 |
| QAOA variant | Vanilla (chosen in month 5: warm start and CVaR were no better from N = 6 up) |
| Depths | 1 and 2 |
| Parameters | Trained noiselessly in simulation (COBYLA, INTERP depth growth, 3 restarts) |
| Shots | 4,000 per circuit |
| Transpilation | `optimization_level=3`, best of 20 seeds by CZ count (month 5: up to 18% fewer CZ than one seed; a line swap strategy used 60-130% more) |
| Submission | One `Batch`, `SamplerV2`, no error mitigation |

That is 40 circuits. Expected CZ counts from month-5 tuning: about 27 (N = 4, depth 1), 58 (N = 4,
depth 2), 63 (N = 6, depth 1) and 149 (N = 6, depth 2).

## Budget

At roughly 1 ms per shot including reset, 40 × 4,000 shots is about 2-3 minutes of QPU time. The
Open Plan allows 10 minutes per 28-day window. Before the real run, submit one N = 4 circuit and
read its reported usage to confirm the estimate. That test job uses development instances and is
not analysed.

## What is reported (descriptive, no confirmatory test)

For every circuit, on hardware and, for the same circuits, under the `FakeKingston` noise model and
noiselessly:

- probability on the exact optimum, and its lift over uniform random sampling;
- share of feasible samples;
- expected cost over feasible samples, relative to the optimum;
- whether the best of 4,000 samples is the optimum;
- whether QAOA's feasible samples beat the per-robot heuristic (each robot's own optimum).

The hardware-to-simulation gap is the quantity of interest. All 40 circuits are reported; none
is dropped or re-run unless the job fails outright, in which case the whole batch is resubmitted
once and the failure is logged.

## Safeguards in the runner

- It refuses to run on hardware without `--confirm-frozen` and the final pool file.
- Instances are drawn by a fixed seeded rule; nothing is chosen by looking at probabilities.
- `--dry-run` runs the identical pipeline on development instances with the noise model. It was
  tested on 1 November 2026 (N = 4, depth 1: 27 CZ gates, 91% feasible, optimum probability 0.078
  against 0.087 noiseless).
