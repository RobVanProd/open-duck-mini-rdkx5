# Winner V173 lexicographic-tangent CPU preregistration

- Status: `PREREGISTERED_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT`
- Actor branches are fixed: reward descent before any real cost, cost descent on positive-cost batches, and cost-tangent reward descent on later zero-cost batches.
- Actor updates use the inherited `3e-4` learning rate and `1.0` global-norm cap directly; Adam cannot rotate the actor direction.
- Reward/cost critics retain Adam. The V127 dual is disabled and pinned exactly to zero.
- Passing the 1,024-step CPU contract earns only a nominal CPU behavior screen. No hosted run, candidate, robustness matrix, Gate 5, RDK-X5, or robot.
