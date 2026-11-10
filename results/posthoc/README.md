# Post-hoc analyses (not pre-registered)

Run after the final results, in response to review. Scripts: `scripts/posthoc_review.py`
(stages `match`, `alpha`, `grid`, `deadline`), `scripts/posthoc_safety_stats.py`,
`scripts/qaoa_baselines.py` (-> `results/final/qaoa_baselines.csv`), `scripts/make_posthoc_figures.py`,
`scripts/make_halt_figure.py`.

| File | Content |
|---|---|
| `match_raw.csv.gz`, `match_sym.csv` | development seeds: kappa* of the per-robot rule under the symmetric operator-error model (5.42 at N = 6, 5.54 at N = 8) |
| `alpha.csv.gz` | final seeds, alpha = 0.9, answers drawn per question: pre-registered and symmetric cost, matched rules, risk caps eps = 0.005/0.01/0.02 |
| `safety_stats.csv` | crossing encounters, distinct crossing scenarios, Clopper-Pearson bounds per encounter and per scenario, epoch- and scenario-cluster bootstrap bounds of the collision difference |
| `grid.csv.gz` | alpha in {0.8..1} x C/tau_s in {2.5..50}, N = 6 noisy, 300 epochs |
| `deadline.csv.gz` | joint execution mode without the queue term (q = 0, kappa swept) vs the joint solver, N = 6 and 8, noisy, alpha = 1, 1,000 final epochs |

Headline numbers: coordinating questions saves 0.068 s (N = 6, 95% CI 0.045-0.090) and 0.052 s
(N = 8, 0.034-0.070) per robot over the per-robot rule applied at the deadline; deciding at the
deadline instead of early saves 2.89 and 3.02 s.
