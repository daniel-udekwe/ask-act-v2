# Month 4: what coordination buys, and QAOA on the queue formulation

Development seeds only (scenario pool 4000-4099; epoch blocks 4 300 000+ and 4 400 000+).
Everything here is exploratory. Changes agreed on 1 Nov and now in the proposal: RQ1 compares
policies at matched question rates; the operator queue term replaces the hard budget (which
becomes an ablation); the operator cost per question κ is swept.

## 1. Pareto study (`scripts/pareto.py`, `results/pareto_summary.md`)

Closed loop, 500 paired epochs per point, N = 6 and 8, nominal and noisy tracking, conventional
and decision-aware calibration. Two policy families, each swept over κ = 0.5 to 7
(ask cost = 1.5 + κ, collision cost C = 100, unnecessary-stop cost 10):

- **Per-robot rule.** Each robot applies its own cost-model optimum, which is a band from
  (1.5 + κ) / 100 to 1 − (1.5 + κ) / 10, and shares the serial operator.
- **Joint, queue.** The exact joint solver with q = 1.5 per pair of askers. A second sweep holds
  κ = 0.5 and varies q from 0 to 6.

Both families cover the full range from about 0 to 8 questions per epoch. Figures:
`results/pareto_decision-aware.png`, `results/pareto_conventional.png`.

### Result: at the same question rate, coordination saves time, not collisions

Interpolating the per-robot curve at each joint point's question rate:

| N | Tracking | Calibration | Delay saved per robot, mean (s) | Range (s) | Collision difference, mean (pp) |
| --- | --- | --- | --- | --- | --- |
| 6 | noisy | conventional | 0.51 | −0.02 to 0.85 | −0.02 |
| 6 | noisy | decision-aware | 0.58 | −0.02 to 0.94 | 0.00 |
| 6 | nominal | conventional | 0.87 | −0.04 to 1.41 | −0.09 |
| 6 | nominal | decision-aware | 1.01 | −0.04 to 1.42 | −0.04 |
| 8 | noisy | conventional | 0.59 | 0.02 to 0.90 | +0.04 |
| 8 | noisy | decision-aware | 0.65 | 0.02 to 0.94 | +0.01 |
| 8 | nominal | conventional | 0.95 | 0.00 to 1.41 | −0.30 |
| 8 | nominal | decision-aware | 1.07 | 0.00 to 1.42 | −0.08 |

- **Delay.** The joint solver's delay curve lies below the per-robot curve across the whole
  range. The gap is largest when questions are scarce: about 0.9 s per robot under noise and
  1.4 s in nominal tracking. The gap vanishes at the top, where every uncertain robot asks
  anyway and the two policies coincide.
- **Collisions.** Across 96 matched comparisons (McNemar exact), none survives correction. The
  smallest p is 0.008: at N = 8, nominal tracking, conventional calibration, the joint solver had
  8 fewer colliding robots. Under noise both curves sit on the same floor.
- **The floor is the predictor, not the policy.** Under noise, about 1% of crossing robots
  collide whenever questions are expensive. Those robots never ask or stop: their probability at
  the deadline is below about 0.09, where going is cheaper than stopping at C = 100. These are
  confidently wrong predictions in the low tail. Only cheap questions (go threshold 0.02) get
  under the floor (0.06% at N = 6).
- **Why coordination saves time.** When questions are scarce, a per-robot rule narrows every
  robot's band the same way, so more robots stop. The joint solver spends the questions on the
  robots whose answer saves the most and lets the rest act. The delay figures already include
  the joint robots' hold at the deadline (at most 1 s; 0.27-0.35 s on average in month 3).

### Implications for the hypotheses

H1 as now written (fewer collisions at a matched question rate) will very likely fail: on
development data there is no collision difference to find. The supported claim is about delay.
I recommend restating H1 before the freeze:

> At a matched question rate, the queue-aware joint solver gives lower mean delay per robot than
> per-robot rules tuned to ask equally often, with a collision rate no more than 0.5 percentage
> points higher (non-inferiority), under noisy tracking.

This mirrors the Ask or Act H3 design (superiority on cost, non-inferiority on safety). The
development data suggest it holds with margin, but that is exactly why it must be fixed now and
tested only on the reserved seeds.

## 2. QAOA on the queue formulation (`scripts/queue_qaoa.py`, `results/queue_qaoa_summary.md`)

Six real-probability instances per size (noisy tracking, decision-aware calibration), each
formulation scored against its own exact optimum. Noiseless, depth 3, 1,024 shots:

| N | Formulation | Qubits | QUBO optimum is the true optimum | Feasible samples | Lift over random (median) | Expected feasible cost above optimum |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | Queue | 8 | 6 of 6 | 99.9% | 16× | 25% |
| 4 | Budget, slack | 10 | 6 of 6 | 91.7% | 7× | 241% |
| 4 | Budget, unbalanced | 8 | 5 of 6 | 69.8% | 16× | 37% |
| 6 | Queue | 12 | 6 of 6 | 99.4% | 63× | 24% |
| 6 | Budget, slack | 14 | 6 of 6 | 87.1% | 10× | 328% |
| 6 | Budget, unbalanced | 12 | 3 of 6 | 33.7% | 63× | 29% |
| 8 | Queue | 16 | 6 of 6 | 99.0% | 252× | 18% |
| 8 | Budget, slack | 18 | 6 of 6 | 59.3% | 8× | 353% |
| 8 | Budget, unbalanced | 16 | 4 of 6 | 34.5% | 253× | 19% |

- **The queue formulation is the best QAOA target on every measure.** It needs the fewest
  qubits, its ground state is always the true optimum, and almost every sample is feasible. Its
  only constraint is that a robot cannot both ask and stop.
- **Unbalanced penalization matches its lift and gate count** (both are dense among the ask
  variables), but its optimum is wrong in 2-3 of 6 instances at N = 6-8. Two-thirds of its
  samples break the budget.
- **The slack budget is the worst target**: 2 extra qubits, the lowest lift, and an expected
  feasible cost 3.5-4.5 times the optimum's.
- **H2 as restated is met on development data** for the queue formulation: lift of at least 10×
  and a feasible expected cost below random sampling's, in every N ≤ 8 cell at depth 3.
- **Absolute numbers stay small.** At N = 8 the optimum gets 0.43% of samples (about 4 in
  1,024). QAOA concentrates probability far better than chance but is nowhere near a solver.

Under the `ibm_kingston` noise model (3 instances, 2,000 shots, depths 1-2):

| N | Formulation | Depth | CZ gates | Feasible, noiseless | Feasible, noisy | Optimum probability, noiseless | Optimum probability, noisy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | Queue | 2 | 60 | 98.5% | 88.2% | 0.052 | 0.046 |
| 4 | Budget, slack | 2 | 142 | 84.2% | 75.4% | 0.016 | 0.015 |
| 6 | Queue | 1 | 77 | 93.4% | 83.5% | 0.0052 | 0.0042 |
| 6 | Queue | 2 | 157 | 96.4% | 77.9% | 0.0119 | 0.0062 |
| 6 | Budget, slack | 2 | 278 | 70.8% | 57.7% | 0.0019 | 0.0028 |

Noise costs the queue formulation 10-19 points of feasibility. At N = 6 depth 2 it also halves
the probability on the optimum, but that is still about twice the slack budget's noiseless
value with less than 60% of its gates. The N = 6 optimum probabilities rest on 4-12 counts in
2,000 shots, so treat them as rough.

## Decisions for you

1. **Restate H1** as delay superiority with collision non-inferiority (wording in section 1).
2. **Fix the primary κ** before the freeze. The joint solver's advantage is largest when questions
   are scarce (high κ), so this choice shapes the headline number. The value should come from a
   stated judgment about operator time, not from these results.
3. **Month 5 plan:** warm-start and CVaR QAOA on the queue formulation, N = 10 (20 qubits),
   transpilation tuning to cut CZ count, and the pre-registered hardware instance list for
   `ibm_kingston`.
