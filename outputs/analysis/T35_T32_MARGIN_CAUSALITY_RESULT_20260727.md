# T35 T32 margin-causality result

status: `PASS_T35_T32_MARGIN_NOT_SUFFICIENT_CAUSE`

decision: `ATTRIBUTE_T32_CONTINUED_TRAINING_ACTOR_STATE_DRIFT`

- wrapped intervention events: `4`
- pre-margin cell executed: `True`
- pre-margin cell green: `False`

The wrapped and pre-margin traces are byte-exact through tick 156. The first
margin intervention is tick 157. Removing the margin changes the failed
494-tick rollout into a complete 600-tick walk, but the raw policy saturates
on 0.666667% of ticks (four margin events), so it still fails the frozen
zero-saturation replacement-quality rule.

The hard clip contributes to the fall, but removing it does not produce a
green policy. The later checkpoint's actor drift is therefore sufficient to
keep T32 closed; the next mechanism must preserve behavior while keeping the
actor inside the margin rather than applying another post-hoc clamp.

T32 remains closed. No training, hosted compute, Gate 5, RDK-X5, robot, torque, or motion is authorized.
