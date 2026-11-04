# Final results: summary for the authors (4 November 2026)

Pre-specified outcomes are in `REPORT.md`; this note only summarises them and points out what the
exploratory tables show. Exploratory statements are descriptive.

## Confirmatory
- **H1a, H1b supported.** At a matched question rate the joint solver saves 2.95 s (N = 6) and
  3.07 s (N = 8) per robot; no collisions for either method.
- **H2 met.** 20/20 instances at N = 4, 6, 8 (median lift 16x, 62x, 215x).
- **H4a, H4b not supported.** 1.8 s faster, but collision bound 1.68 / 1.28 pp > 0.5 pp; N = 8
  question rates differ by 15.8% (deviation). See `POSTHOC_H4.md`.

## Gazebo final validation (N = 4, 20 epochs, final seeds): all four criteria MET
- Collision outcome agrees in 100% of 320 robot-runs (no collisions either side).
- Independent rule: question count agrees in 98.8% of robot-runs.
- Joint: in 100% of 40 epochs the Gazebo assignment costs at most one question more than offline
  (max 2.15 units); raw per-robot action agreement 88.1%.
- Mean delay difference 0.10-0.20 s per condition and method (limit 0.5 s). No infrastructure
  failures excluded.

## Exploratory observations
1. **The fixed Ask or Act band is faster than the joint solver** (noisy, decision-aware: 3.16 vs
   3.80 s at N = 6), with no collisions, but asks 3x as often (6.0 vs 2.0 questions per epoch)
   and leaves 0.8 questions per epoch unanswered (joint: 0.0). The joint solver's gain is in
   operator load, not in delay against an operator-heavy rule.
2. **Calibration matters for safety.** With α = 1, the only collisions in the whole study occur
   with raw (uncalibrated) probabilities and noisy tracking: 0.27-0.48% of crossing robots for
   every joint variant. Conventional and decision-aware calibration give zero. Decision-aware
   against conventional: no difference at α = 1 (0 vs 0); at α = 0.9 12 vs 20 discordant
   collisions (McNemar p = 0.22).
3. **Imperfect answers.** Every joint variant that asks at moderate p collides at α = 0.9 (about
   1-1.7% noisy, 0-0.5% nominal); α-aware rules at κ ≥ 1.5 never collide. A mis-specified solver
   (assuming α = 1) is no worse than the α-aware one in collisions (1.42% vs 1.36% at N = 6), but asks
   3x as often. The answer stream is keyed on the scenario, so these α = 0.9 rates rest on few
   distinct wrong answers (`POSTHOC_H4.md`).
4. **Budget ablation.** A hard budget B = ⌈N/3⌉ performs like the queue term (N = 6: 3.81 vs 3.80 s;
   N = 8: 3.86 vs 3.93 s, 3.0 vs 2.2 questions).

## Verification
The exploratory stage was run on D. Udekwe's machine (28 cores). Spot checks of four epochs across
three cells reproduce it exactly here, and its confirmatory-method rows equal the confirmatory
stage robot for robot (56,000 rows).
