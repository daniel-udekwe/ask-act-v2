# Month 2: real probabilities and hardware noise

All results use development seeds only (scenario pool 4000-4099). Nothing here touches the
reserved final pool (8000-8099). Every result is exploratory.

## What was done

1. Regenerated the Ask or Act dataset and retrained the MLP and calibrators with the
   repository's own scripts (scikit-learn 1.9). The training set matches the paper
   (23,344 samples) and the paper's calibration pattern reproduces: decision-window ECE under
   noise is 0.060 for conventional and 0.014 for decision-aware recalibration (paper: 0.056, 0.017).
2. Extracted each scenario's smoothed calibrated probability at the 0.6 m deadline with the
   unchanged offline simulator (`scripts/extract_deadline_probs.py`), for raw, conventional and
   decision-aware calibration: about 700 decision-relevant scenarios per condition.
3. Scored fleet epochs against ground-truth intent (`scripts/epoch_eval.py`, 500 epochs per cell).
4. Swept the collision cost (`scripts/cost_ratio_sweep.py`).
5. Ran QAOA under the `ibm_kingston` noise model (`scripts/noisy_qaoa.py`).

## Findings

**The question budget binds almost always.** At the deadline most robots are still in the ask
band, so with B = ceil(N/3) the budget binds in 82-100% of epochs. Coordination is not a corner case.

**The default costs are unsafe, and this is a model issue, not a solver issue.** Reproducing the
symmetric [0.2, 0.8] band forces collision cost = unnecessary-stop cost (C = tau_s). A robot
denied a question then goes whenever p < 0.5. With these costs the exact joint solver collided
with 35-60% of crossing robots, against 2-32% for the independent Ask or Act rule, which falls
back to stopping. See `results/epoch_summary.md`.

**With an asymmetric cost the joint optimum is much safer.** N = 6, noisy tracking, no corridor:

| Calibration | Independent rule | Exact, C = 10 | Exact, C = 50 | Exact, C = 100 |
| --- | --- | --- | --- | --- |
| Raw | 32.4% | 52.2% | 18.7% | 7.3% |
| Conventional | 18.0% | 56.1% | 2.1% | 0.6% |
| Decision-aware | 1.9% | 42.9% | 1.4% | 0.8% |

Unnecessary stops per epoch at C = 100 are close to the independent rule's for the calibrated
variants (1.65 against 1.19-1.63). See `results/cost_ratio_sweep.md`.

**Calibration matters most at moderate cost ratios.** With the exact solver, decision-aware
beats conventional calibration in every cell at C = 10 (McNemar p < 1e-13). At C = 100 the optimizer
turns conservative and the gap closes. RQ3's answer will depend on the cost ratio, so the ratio
must be fixed before the freeze, from a stated value judgment.

**Noise costs QAOA little at N = 4 and more at N = 6.** Under the Kingston noise model:

- N = 4 keeps 83-100% of the noiseless probability on the optimum at every depth.
- N = 6 slack keeps 42-88% and loses feasibility as depth grows (0.89 to 0.65 at depth 3).
- Unbalanced penalization holds up better because its circuits are about half the size.

See `results/noisy_summary.md`. N = 6 rests on 3 instances only. Noisy simulation of the
486-gate depth-3 circuits took about 12 minutes each, so the corridor layout under noise moves to month 3.

## Decisions needed before month 3

1. Collision-to-stop cost ratio (recommended primary C / tau_s = 10, with the sweep as a robustness check).
2. Whether the independent baseline uses the fixed Ask or Act band or the cost model's own band.
3. Hypothesis H2 metric (lift and feasible expected cost, not "found within 5%").
