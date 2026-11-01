# Month 3: multi-robot closed loop

Development seeds only (scenario pool 4000-4099, epoch block 4 200 000+). Everything here is
exploratory. Decisions taken on 1 Nov: C = 100 (a collision costs ten unnecessary stops), the
independent baseline keeps the fixed Ask or Act band, and H2 is restated as lift over random sampling.

## The simulator

`fleet_qubo/fleet_sim.py` steps N robots in lockstep, each driving its own Ask or Act scenario.
The per-robot step logic is copied from `simulate_policies.simulate()`, and a test checks that one
robot reproduces it exactly (outcome, delay, minimum distance, collisions, questions, stopped time)
at any clock shift. A second test checks that the probability each joint robot reports at its
deadline equals the value extracted in month 2.

What it simulates:

- **One operator** answers all questions in arrival order, 1.5 s each. An unanswered question
  times out after 5 s and the robot falls back to the cautious rule, as in Ask or Act.
- **Decision epochs.** Robots reach their deadlines within a 1 s window. In joint mode each robot
  holds at its deadline until all have arrived, then the solver assigns go, stop or ask.
- **Congestion** (both neighbours on a single corridor halted at once) is measured, not simulated:
  robots run on separate lanes, so a halted robot does not physically block another.

## Methods (paired: same scenarios, timing, noise and answers)

| Method | What it is |
| --- | --- |
| independent | Unchanged Ask or Act policy, fixed band [0.2, 0.8], shared operator |
| independent_costband | Same, but each robot applies the C = 100 rule alone (go below p = 0.02) |
| joint_free | Joint pipeline (hold at deadline, no early commits) with no coupling |
| joint_none | Exact joint solver, hard budget B = 2 |
| joint_single | Exact joint solver, budget + single-corridor congestion coupling |
| joint_queue | Exact joint solver, no budget; each pair of askers costs one service time of waiting |

## Results (N = 6, 1,000 epochs per cell, noisy tracking)

| Calibration | Method | Collisions (%) | Questions / epoch | Unanswered / epoch | Mean delay (s) |
| --- | --- | --- | --- | --- | --- |
| Decision-aware | independent | 2.2 | 5.74 | 0.78 | 3.39 |
| Decision-aware | independent_costband | 0.3 | 5.88 | 0.82 | 3.48 |
| Decision-aware | joint_free | 0.3 | 5.88 | 0.78 | 3.47 |
| Decision-aware | joint_queue | 1.2 | 2.88 | 0.01 | 3.95 |
| Decision-aware | joint_none | 1.2 | 2.00 | 0 | 4.07 |
| Decision-aware | joint_single | 1.7 | 2.00 | 0 | 4.06 |
| Conventional | independent | 18.0 | 4.82 | 0.52 | 2.78 |
| Conventional | independent_costband | 0.3 | 5.90 | 0.84 | 3.47 |
| Conventional | joint_queue | 0.6 | 3.19 | 0.04 | 3.95 |
| Raw | independent | 31.7 | 3.66 | 0.26 | 2.28 |
| Raw | independent_costband | 1.3 | 5.58 | 0.74 | 3.46 |
| Raw | joint_queue | 5.2 | 3.28 | 0.07 | 3.70 |

Full tables, nominal results and paired tests: `results/closed_loop_summary.md`.

## What it means

**1. Against the fixed Ask or Act band, every joint method wins** (fewer collisions, fewer
questions; McNemar p < 1e-4 in every noisy comparison). That is H1 as written, but it is the
wrong comparison: most of the gain comes from the cost ratio, not from coordination.

**2. The cost ratio does the work.** Giving each robot the C = 100 rule on its own cuts
collisions under noise from 31.7 / 18.0 / 2.2% to 1.3 / 0.3 / 0.3% (raw / conventional /
decision-aware), for about 0.1-1.2 s more delay per robot.

**3. Early commits do not matter.** `independent_costband` and `joint_free` give identical
collisions, and their delays differ by 0.02 s or less.

**4. Coordination trades safety and time for operator load.** Going from `joint_free` to
`joint_queue` halves the questions (5.9 to 2.9 per epoch) and almost removes unanswered ones.
It also adds 0.5 s of delay per robot and, under noise, 9-31 more collisions per 1,000 epochs
(p < 0.004). The reason: in closed loop an extra question is cheap. It waits in the queue, and
if it times out the robot stops cautiously. The QUBO instead treats each question it denies as a
forced stop-or-go choice. The hard budget (`joint_none`) is the most extreme form of this.

**5. Corridor coupling at w = 2 buys almost nothing.** `joint_single` against `joint_none`
reduces congestion by 0.1 s per epoch and adds collisions under noise (15 against 0, p = 6e-5).

**6. Calibration still matters behind the optimizer, but less.** Under the fixed band,
decision-aware calibration beats conventional calibration by 538 collisions to 0. Behind the
C = 100 optimizer both reach about 0.3%. With a hard budget, conventional calibration does
slightly better (0.9% against 1.7%). RQ3's answer depends on the cost ratio.

## Recommended changes before the freeze

1. **Reframe RQ1 as a trade-off.** The question becomes: at a matched question rate, does
   joint allocation give fewer collisions and less delay than per-robot rules that ask less?
   Here a per-robot rule asks less by narrowing its own band. Report the Pareto frontier of
   questions against collisions and delay, sweeping the queue cost q (joint) and the band
   width (independent).
2. **Replace the hard budget with the queue term** as the main formulation. It models the
   operator directly and needs no slack qubits, so N robots use 2N qubits: 12 instead of 14 at
   N = 6. The test suite checks that its ground state is the true optimum. Keep the budget
   version as an ablation.
3. **Make κ (operator effort per question) the knob that matters.** Joint allocation is worth
   it only if operator time is costly. The study should state κ from a stated value judgment,
   and sweep it.
4. **Drop the corridor-congestion coupling unless robots physically block each other.** That
   needs shared lanes in the simulator or Gazebo, which is month 4-5 work.

## QAOA on the corridor layout under noise

N = 6 on a single corridor, 3 instances, depths 1-2, 2,000 shots, `ibm_kingston` noise model:

| Encoding | Depth | Qubits | CZ gates | Feasible, noiseless | Feasible, noisy | Lift over random, noisy |
| --- | --- | --- | --- | --- | --- | --- |
| Slack | 1 | 14 | 193 | 0.64 | 0.56 | 2.0 |
| Slack | 2 | 14 | 509 | 0.82 | 0.62 | 6.1 |
| Unbalanced | 1 | 12 | 150 | 0.83 | 0.69 | 10.9 |
| Unbalanced | 2 | 12 | 359 | 0.90 | 0.72 | 12.3 |

Corridor coupling roughly doubles the two-qubit gate count against the budget-only problem at
the same depth. Noise costs 8-20 points of feasibility. Probabilities on the optimum are about
0.001-0.003, i.e. 2-6 counts in 2,000 shots, so the lift values are rough. The queue formulation
(12 qubits, no slack) is the natural next QAOA target. Full table: `results/noisy_summary.md`.
