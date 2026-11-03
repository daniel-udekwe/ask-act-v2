# Development results after the probability fix (3 November 2026)

All closed-loop development results before this date used Ask or Act's `predict()`, which froze the
crossing probability once 40 observations were held (see `ANALYSIS_PLAN.md` §1). This note re-runs
the studies that feed the analysis plan with the corrected policy and compares them with the
frozen-probability results (archived in `results/frozen_p/`). Development seeds only.

## 1. Deadline probabilities

With the probability updating to the deadline, crossing pedestrians are recognised much more
reliably (`results/deadline_probs.csv`, noisy tracking, decision-aware calibration):

| | frozen | corrected |
|---|---|---|
| lowest p for a crossing pedestrian | 0.000 | 0.241 |
| 5th percentile, crossing | 0.222 | 0.316 |

Under the cost model a robot drives on only below p = τₛ/(C + τₛ) = 0.091, so no crossing
pedestrian at the deadline is now low enough to drive past.

## 2. Collisions (α = 1, perfect answers)

| Study | robot-runs | collisions, frozen | collisions, corrected |
|---|---|---|---|
| Pareto, both families, N = 6 and 8 (`results/pareto_summary.md`) | 560,000 | 1,528 | **0** |
| Ask or Act fixed band [0.2, 0.8], N = 6 (`results/dev_checks.md`) | 4,800 | (collided) | **0** |

The simulator does still detect collisions: robots that never stop hit 120 of 120 crossing
pedestrians.

**Consequence:** with perfect answers, collisions no longer separate any methods. The collision
part of H1 is met trivially, and H3 (collisions, decision-aware against conventional calibration)
has no events to test.

## 3. Delay at a matched question rate (H1)

`results/dev_matching.csv` (N = 6 and 8, noisy, decision-aware, 500 epochs, seeds 4 900 000+):

| N | joint questions/epoch | matched κ* | rule delay at κ* (s) | joint delay (s) |
|---|---|---|---|---|
| 6 | 2.03 | **5.95** | ≈ 7.0 | 3.78 |
| 8 | 2.18 | **6.15** | ≈ 7.0 | 3.95 |

Delay saved along the Pareto frontier (mean over matched points, s per robot):

| | frozen | corrected |
|---|---|---|
| N = 6, noisy, decision-aware | 0.58 | 1.81 |
| N = 8, noisy, decision-aware | 0.65 | 2.04 |
| N = 6, nominal, decision-aware | 1.01 | 0.94 |

Caution: the rule's question rate falls steeply between κ = 5.75 (2.35/epoch) and κ = 6.25
(1.38/epoch), so on final data the 10% matching check in the plan may fail. The plan already says
this is reported, not re-tuned.

## 4. Imperfect answers (α = 0.9)

| Solver and rule | method (decision-aware) | questions/epoch | collisions / crossing | delay (s) |
|---|---|---|---|---|
| assume α = 1 (`dev_checks.md`) | rule κ = 5.95 | 2.04 | 0 / 690 | 6.80 |
| | joint κ = 1.5, q = 1.5 | 2.11 | 7 / 690 | 3.97 |
| α-aware (`dev_alpha_aware.csv`) | rule κ = 1.5 | 2.55 | 0 / 671 | 5.18 |
| | rule κ = 3 | 2.38 | 0 / 671 | 6.39 |
| | joint κ = 1.5, q = 1.5 | 0.62 | 0 / 671 | 4.32 |

When the solver wrongly assumes perfect answers, it asks about likely-crossing pedestrians and a
wrong "not crossing" answer sends the robot into them (about 1% of crossing robots, above the
0.5 pp margin). When the solver knows α, it asks far less and collisions return to about zero
(0 to 1 of 671, both calibrations).

## 5. QAOA (H2), queue formulation, κ = 1.5

`results/qaoa_variants.csv`, vanilla, depth 3, noiseless, 6 development instances per N:

| N | lift (frozen) | lift (corrected) | feasible share | H2 met |
|---|---|---|---|---|
| 4 | 15.9 | 15.6 | 0.996 | 6 / 6 |
| 6 | 63.5 | 62.9 | 0.995 | 6 / 6 |
| 8 | 251 | 253 | 0.987 | 6 / 6 |

QAOA performance is essentially unchanged: it depends on the probabilities only through the
instance costs. The vanilla circuit remains the right choice for hardware. Not re-run: N = 10
variants and the `ibm_kingston` noise-model study (both exploratory; still pre-fix in their
summaries).

## 6. Proposed changes to the analysis plan (for D. Udekwe and Q. Guo)

1. **Fill κ\*:** 5.95 (N = 6) and 6.15 (N = 8).
2. **H1 stays as written** (delay superiority, collision non-inferiority at α = 1). Expect the
   collision part to hold with zero or near-zero events; report it as such.
3. **New confirmatory H4, α = 0.9 with α-aware solver and rule:** `joint` against the α-aware
   rule matched to the joint question rate; same two-part test as H1. This is where the
   collision margin has real content. κ* for this would be matched on new development seeds
   before freezing.
4. **H3:** replace the collision endpoint, as there are no collisions. Options:
   (a) mean delay of `joint`, decision-aware against conventional (development, interpolated to κ = 1.5:
   about 3.80 against 3.73 s, i.e. conventional slightly faster); (b) collisions under α = 0.9 (H4 setting), likely
   too few events for power; (c) move calibration to the exploratory list. Our recommendation is (c),
   since development shows no meaningful difference for the joint solver.
5. **Keep the Ask or Act band (`aoa_band`) as a reference**: it asks about 6 questions per
   epoch at N = 6 against 2 for `joint`, with similar delay (3.2 against 3.8 s).

## 7. Implication for the Ask or Act paper

The same frozen probability is in the Ask or Act closed-loop evaluation. Its collision results
are likely to change materially after the fix. The Ask or Act repository has not been modified.
