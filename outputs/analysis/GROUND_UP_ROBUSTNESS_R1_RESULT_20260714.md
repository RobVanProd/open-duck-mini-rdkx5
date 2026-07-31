# Ground-Up Robustness R1 Result

status: `PASS_ROBUSTNESS_R1_NO_ADVANCE`
decision: `CLOSE_FROZEN_POLICY_AT_R1`

| fit | step | x=0 | nominal | worst tracking | min vx | pass |
|---|---:|---|---|---:|---:|---|
| `p30` | 512000 | `True` | `True` | 0.180822033 | 0.083376151 | `True` |
| `p30` | 1024000 | `True` | `True` | 0.181667066 | 0.095189543 | `True` |
| `p31_34` | 512000 | `True` | `False` | 0.180555040 | 0.085535203 | `False` |
| `p31_34` | 1024000 | `True` | `False` | 0.183141637 | 0.097717078 | `False` |

All six P31/34 moving cells retain gait, tracking below .20 rad, and zero saturation, but exceed that fit's left-ankle 1.50 rad/s limit by .250001 rad/s. The guarded policy was built around the P30 left-ankle 1.75 rad/s limit.

R1 passing authorizes only the R2 evaluator contract. It does not authorize R2 behavior, later stages, training, RDK-X5, or robot access.
