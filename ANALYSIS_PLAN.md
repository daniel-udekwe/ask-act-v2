# Fleet Ask or Act with QAOA: pre-specified analysis plan

**Status: DRAFT for review by D. Udekwe and Q. Guo. Not yet frozen.**
Items marked `[DEV]` are filled from development data before freezing.
Changes after the probability fix (agreed by D. Udekwe and Q. Guo, 3 November 2026; see
`DEV_RERUN.md`): H3 moved to the exploratory list; new confirmatory H4 at α = 0.9.

This plan is fixed before any final run. Every result listed here is reported, whether or not it
supports our expectations. Any change after the final runs start is recorded in the deviations log
at the end, with its reason.

## 1. Frozen version

- Code: git tag `v2-prereg` in github.com/daniel-udekwe/ask-act-v2 (commit hash recorded at tagging).
- Ask or Act code used by the simulator: github.com/daniel-udekwe/turtlebot3-ask_or_act, commit
  `c0f46e3`, with one correction applied in this repository: `FleetPolicy.predict()` fixes the
  prediction cache, which in the original froze the crossing probability once the
  40-observation history was full (found 3 November 2026; see `fleet_qubo/fleet_sim.py`).
- Predictor: `predictor/intent_model.pkl` (SHA-256 prefix `788ea654e61b31db`), the Ask or Act MLP and
  calibrators rebuilt with that repository's own scripts under scikit-learn 1.9.1.
- Software: Python 3.13, numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, scikit-learn 1.9.1,
  Qiskit 2.6.1, Qiskit Aer 0.18.2, qiskit-ibm-runtime 0.51.0, OR-Tools 9.15.

## 2. Fixed settings

| Setting | Value |
| --- | --- |
| Scenarios | Ask or Act cafe scenarios: 8 families, nominal and noisy tracking |
| Robot, deadline, engagement | As Ask or Act: 0.18 m/s, decision deadline 0.6 m, engagement 1.0 m |
| Predictor and calibration | MLP; raw, conventional isotonic, decision-aware isotonic, recalibrated per condition |
| Decision epoch | Robots reach their deadlines within a 1 s window; joint robots hold until the epoch closes (all arrived, or 1.5 s) |
| Operator | One operator, first come first served, 1.5 s per question; 5 s answer timeout, then the Ask or Act cautious rule |
| Answer accuracy | α = 1 (main); α = 0.9 (secondary) |
| Cost model | Collision C = 100, unnecessary stop τₛ = 10, ask time τₐ = 1.5, operator cost κ = 1.5 |
| Queue term | q = 1.5 per pair of robots that ask |
| Joint solver | Exhaustive search over 3ᴺ action vectors (exact) |
| Fleet sizes | N = 6 and N = 8 (closed loop); N = 4, 6, 8 (QAOA benchmark) |

## 3. Seeds

Development used scenario seeds 4000-4099 (and earlier blocks). Final results use only:

| Use | Seeds |
| --- | --- |
| Scenario pool | 8000-8099 in each condition block (10000 × condition index + s) |
| Closed-loop epochs | 8 100 000 + e, e = 0-999 |
| QAOA benchmark instances | 8 200 000 + k, k = 0-19 per N |
| Hardware instances | 8 500 000 + k, k = 0-9 per N (`prereg/HARDWARE.md`) |
| Gazebo validation epochs | 8 700 000 + e, e = 0-19 |

The final pool is built with `scripts/extract_deadline_probs.py --seed-start 8000` only after tagging.

## 4. Methods (closed loop)

All methods are paired: every method sees the same scenarios, timing, tracker noise and answers.

| Method | Description |
| --- | --- |
| `aoa_band` | Ask or Act threshold rule, fixed band [0.2, 0.8] (current practice) |
| `rule_k<κ>` | Each robot's own cost-model optimum (band from κ), sharing the operator; κ ∈ {0.5, 1, 2, …, 7} |
| `rule_matched` | `rule_k<κ*>` with κ* = 5.95 (N = 6) and 6.15 (N = 8) (`results/dev_matching.csv`), matched to the joint question rate |
| `joint` | Queue-aware joint solver, κ = 1.5, q = 1.5 (primary) |
| `joint_k<κ>` | Joint solver at other κ (frontier) |
| `joint_budget` | Joint solver with a hard budget B = ⌈N/3⌉ instead of the queue (ablation) |
| `joint_a` | α-aware joint solver (α = 0.9 in the cost model), κ = 1.5, q = 1.5; run with α = 0.9 answers |
| `rule_a_matched` | α-aware per-robot rule (band from κ and α), κ = `[DEV]` (N = 6) and `[DEV]` (N = 8), matched to `joint_a`'s question rate; run with α = 0.9 answers |

Calibrations: raw, conventional, decision-aware. Conditions: nominal, noisy. 1,000 epochs per cell.

## 5. Metrics

- **Primary:** collision rate on crossing robots; mean delay per robot (s) versus free driving.
- **Secondary:** questions per epoch; unanswered questions per epoch; stopped time with
  non-crossing pedestrians; hold time at the deadline.
- **QAOA:** probability on the optimum and lift over uniform random; feasible share; expected
  cost over feasible samples relative to the optimum; share of samples cheaper than the
  per-robot heuristic; two-qubit gate count after transpilation.

## 6. Hypotheses and tests

The unit of pairing is the epoch: robots in one epoch share the operator and the solver, so
they are not independent.

| | Hypothesis | Test |
| --- | --- | --- |
| H1a | N = 6, noisy tracking, decision-aware calibration: `joint` gives lower mean delay than `rule_matched` (superiority), with a collision rate on crossing robots at most 0.5 percentage points higher (non-inferiority). | Delay: one-sided Wilcoxon signed-rank on paired epoch-mean delays. Collisions: one-sided 95% upper bound of the paired difference (joint − rule), epoch-cluster bootstrap, 10,000 resamples; must be below 0.5 pp. Both parts must hold. |
| H1b | As H1a, for N = 8. | As H1a. |
| H2 | QAOA (vanilla, depth 3, noiseless, 1,024 shots) on the queue formulation: in at least 80% of instances at each N ∈ {4, 6, 8}, the probability on the optimum is at least 10 times uniform random, and the expected cost over feasible samples is below uniform random's. | Descriptive criterion per N, 20 instances each, with Clopper-Pearson 95% intervals on the share. |
| H4a | N = 6, noisy, decision-aware, operator answers correct with probability α = 0.9: `joint_a` gives lower mean delay than `rule_a_matched`, with a collision rate on crossing robots at most 0.5 percentage points higher. | As H1a. |
| H4b | As H4a, for N = 8. | As H1a. |

Holm correction across the delay-superiority p-values of H1a, H1b, H4a and H4b. Each
hypothesis also requires its collision non-inferiority bound. H2 is a descriptive criterion and is
not part of the family. At α = 1 collisions may be zero for both methods; the bound is then 0 pp
and non-inferiority holds, which is reported as such. The matched question rates are reported. If on final
data a matched rule and its joint method differ by more than 10% in questions per epoch, this is reported as
a deviation; κ* is not re-tuned on final data.

## 7. Secondary and exploratory analyses (all reported, none confirmatory)

1. Pareto frontiers of questions per epoch against collisions and delay, for both policy
   families, N = 6 and 8, both conditions and calibrations.
2. α = 0.9 Pareto frontiers for the α-aware methods, N = 6 and 8, both calibrations.
3. `aoa_band` against all other methods.
4. Budget ablation (`joint_budget`) against `joint`.
5. QAOA variants (warm start, CVaR), N = 10, and the budget formulation (slack and unbalanced).
6. QAOA under the `ibm_kingston` noise model, N = 4 and 6, depths 1-2.
7. Calibration (formerly H3): `joint`, N = 6, noisy, decision-aware against conventional
   calibration: collisions (two-sided exact McNemar on paired crossing robots, if any events),
   delay and questions per epoch, at α = 1 and α = 0.9.
8. Mis-specified solver: `joint` (assuming α = 1) run with α = 0.9 answers.

## 8. Hardware

As pre-registered in `prereg/HARDWARE.md` and `prereg/hardware.json`: 40 circuits on
`ibm_kingston` (fallbacks `ibm_marrakesh`, `ibm_fez`), descriptive only.

## 9. Gazebo validation

N = 4, 20 epochs, nominal and noisy, `rule_matched`-type independent rule and `joint`
(`fleet_gazebo/`). Gazebo and the offline simulator use identical inputs, including per-slot
tracker noise. Infrastructure failures (no pedestrian data, a robot that never moved, no
result) are re-run once and reported; persistent failures are excluded and counted.

Agreement criteria `[DEV, after the v2 development validation]`:
- collision outcome agrees for at least 95% of robot-runs (the Ask or Act criterion);
- mean questions per epoch and mean delay per robot within limits set from the v2 run;
- per-robot action agreement reported descriptively, with near-ties identified by the extra
  expected cost of the Gazebo assignment under the offline probabilities.

## 10. Deviations log

| Date | Change | Reason |
| --- | --- | --- |
| 3 Nov 2026 (before freezing) | H3 moved to exploratory; H4a/H4b added | Corrected probabilities give no collisions at α = 1 (`DEV_RERUN.md`) |
