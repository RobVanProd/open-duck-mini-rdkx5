# Ground-Up Stage-One Recipe Tie-Break Preregistration

status: `PREREGISTERED_BEFORE_TIEBREAK_COMPUTE`

The broad rung produced an exact three-way tie between the center, entropy
cost `0.001`, and imitation scale `2.0`. Selecting two by preference would be
unsupported. This extension gives all three the same longer seed-100 evidence.

- Reuse the center's already-recorded 10,035,200 and 12,042,240 checkpoints.
- Retrain `S1ENT_LO` and `S1IMIT_HI` from scratch with training seed `100` to
  12,042,240 steps.
- Evaluate their 10M and 12M checkpoints using the same commands, rollout seeds,
  1.08-second duration, actuator fit, and CPU evaluator.
- Apply the same hard-failure-dominant score key. Training reward is excluded.
- At most two recipes advance to second-training-seed replication.
- If more than two remain exactly tied, there is no tie-break winner and no
  arbitrary promotion.

Only the two noncanonical recipes require new compute; the center is not
rerun. No local GPU, RDK-X5, or robot access is authorized.

