# H4: post-hoc explanation (NOT pre-specified; exploratory)

The pre-specified result stands: H4a and H4b are **not supported**. Delay superiority holds
(1.8 s saved per robot), but the collision non-inferiority bound fails (95% upper bound 1.68 pp at
N = 6, 1.28 pp at N = 8, against a 0.5 pp margin). This note explains why; it changes nothing.

1. **Why `joint_a` collides and the matched rule does not.** Under the α-aware cost model the joint
   solver asks when 0.03 < p < 0.35 (asking costs τₐ + κ + C·p·(1 − α)), accepting a collision risk of
   p(1 − α) per question. The matched rule (κ* ≈ 6) asks only when 0.084 < p < 0.123, i.e. almost only
   about pedestrians who are not crossing, where a wrong answer causes an unnecessary stop rather
   than a collision. Matching the question rate does not match who is asked.
2. **Why development predicted ~0.1% and the final run gave ~1.2%.** Operator answers are drawn from
   a stream keyed on the scenario (as in Ask or Act and the Gazebo coordinator), so a scenario whose
   first answer is wrong gets the same wrong answer in every epoch it appears in. All 92 `joint_a`
   collisions come from 8 such crossing scenarios, each reused 12-27 times. `joint_a` asked about 396
   crossing robots; with independent answers about 40 collisions (0.5% of 7,859 crossing robots)
   would be expected. The development pool happened to contain few such scenarios.
3. **Consequence for inference.** Because of this clustering, the epoch-cluster bootstrap
   understates the uncertainty of every α = 0.9 collision estimate; the effective sample is the
   number of distinct crossing scenarios asked about, not the number of epochs. This applies to the
   α = 0.9 exploratory analyses too.
