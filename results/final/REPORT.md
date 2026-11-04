# Final results (pre-specified analysis, ANALYSIS_PLAN.md)

## Confirmatory: H1a, H1b, H4a, H4b

Noisy tracking, decision-aware calibration. Delay: one-sided Wilcoxon on paired epoch means, Holm across the four. Collisions: crossing robots, joint − rule, one-sided 95% epoch-cluster bootstrap bound (10,000 resamples), margin 0.5 pp.

| hypothesis   |   N | joint   | rule           |   epochs |   crossing_robots |   delay_joint |   delay_rule |   delay_saved |    p_delay |     p_holm |   col_joint_pct |   col_rule_pct |   col_diff_ub95_pp | noninferior   |   q_joint |   q_rule | matching_deviation   | supported   |
|:-------------|----:|:--------|:---------------|---------:|------------------:|--------------:|-------------:|--------------:|-----------:|-----------:|----------------:|---------------:|-------------------:|:--------------|----------:|---------:|:---------------------|:------------|
| H1a          |   6 | joint   | rule_matched   |     1000 |              3321 |         3.798 |        6.752 |         2.954 | 2.061e-165 | 6.651e-165 |           0     |              0 |              0     | True          |     1.99  |    2.144 | False                | True        |
| H1b          |   8 | joint   | rule_matched   |     1000 |              4538 |         3.934 |        7.007 |         3.072 | 1.663e-165 | 6.651e-165 |           0     |              0 |              0     | True          |     2.201 |    2.057 | False                | True        |
| H4a          |   6 | joint_a | rule_a_matched |     1000 |              3321 |         4.349 |        6.152 |         1.803 | 1.803e-165 | 6.651e-165 |           1.355 |              0 |              1.678 | False         |     0.592 |    0.607 | False                | False       |
| H4b          |   8 | joint_a | rule_a_matched |     1000 |              4538 |         4.335 |        6.11  |         1.774 | 1.667e-165 | 6.651e-165 |           1.036 |              0 |              1.278 | False         |     0.748 |    0.63  | True                 | False       |

- H1a: no collisions for either method; non-inferiority holds trivially.
- H1b: no collisions for either method; non-inferiority holds trivially.
- Deviation: H4b questions per epoch differ by 15.8% (joint 0.748, rule 0.630); κ* not re-tuned.

## H2: QAOA on the queue formulation (vanilla, depth 3, noiseless)

|   N |   instances |   passed |   share |   ci_low |   ci_high | criterion_met   |   lift_median |   feasible_share_median |   feasible_gap_median |   random_gap_median |
|----:|------------:|---------:|--------:|---------:|----------:|:----------------|--------------:|------------------------:|----------------------:|--------------------:|
|   4 |          20 |       20 |       1 |   0.8316 |         1 | True            |         15.8  |                  0.9978 |                0.2557 |               5.093 |
|   6 |          20 |       20 |       1 |   0.8316 |         1 | True            |         61.76 |                  0.9967 |                0.2692 |               4.335 |
|   8 |          20 |       20 |       1 |   0.8316 |         1 | True            |        214.8  |                  0.9861 |                0.3668 |               4.232 |

H2 MET (share ≥ 80% at every N ∈ {4, 6, 8}).
