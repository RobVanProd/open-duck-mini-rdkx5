# Ground-Up Stage-One Mixture Center Trajectory

status: `HOLD_TRANSIENT_PARTIAL_EMERGENCE_NO_RECIPE_WINNER`

## Result

The corrected-frame, stage-one-mixture center recipe is a useful search center,
not a selected recipe. Its seed-100 training trajectory reached partial moving
behavior, but never passed the frozen two-rollout checkpoint emergence gate at
6M, 8M, 10M, or 12M steps.

| checkpoint steps | both x=0 finite | moving gate | x=0.08 local vx, seeds 100/101 (m/s) | termination |
|---:|---|---|---|---|
| 6,021,120 | yes | fail | `-0.03310 / -0.02959` | complete / complete |
| 8,028,160 | yes | fail | `+0.04294 / -0.04420` | complete / complete |
| 10,035,200 | no | fail | `+0.35428 / -0.03320` | fall / complete |
| 12,042,240 | yes | fail | `+0.02353 / -0.01947` | complete / complete |

At 8M and 12M, moving rollout seed 100 had positive local forward velocity,
while seed 101 remained negative. At 10M the high positive seed-100 velocity
ended in a fall and cannot be counted as improvement. No evaluated checkpoint
passed both moving seeds, and there is no qualifying pair of consecutive
checkpoints.

## Decision

The earlier `STAGE1MIX4` result remains evidence that the command mixture
improves finite training behavior relative to the earlier controls. It does not
show that learning rate `3e-4`, entropy `0.005`, and imitation scale `1.0` are
the best recipe. Policy-family search is paused while the preregistered local
recipe search tests one-factor neighbors under equal compute and the same
offline evaluator.

Training reward is excluded from this decision. This report does not authorize
RDK-X5 access, deployment, robot access, torque, or motor activity.
