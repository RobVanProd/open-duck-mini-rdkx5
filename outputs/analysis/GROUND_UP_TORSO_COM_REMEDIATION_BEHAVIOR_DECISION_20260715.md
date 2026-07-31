# Ground-Up Torso-COM Remediation Behavior Decision

status: `PASS_TORSO_COM_REMEDIATION_EVALUATION_NO_ARM_ADVANCES`
decision: `CLOSE_EXACT_TARGETED_COM_FORMULATION_NO_WINNER`
selected arm: `NONE`
training reward used for selection: `False`

| arm | matrices | cells | endpoint tracking worst | endpoint min vx | nominal tracking worst | pass |
|---|---:|---:|---:|---:|---:|---|
| `U_CURRICULUM` | 4/12 | 20/48 | 0.179574585 | -0.410234554 | 0.181958497 | `False` |
| `A05_DIRECT` | 4/12 | 20/48 | 0.183277678 | -0.363655473 | 0.182503945 | `False` |
| `U05_DIRECT` | 4/12 | 20/48 | 0.180909431 | -0.405355284 | 0.179710203 | `False` |

No arm passes both checkpoints across every frozen cell. The exact targeted-COM formulation is closed without promoting a closest arm.
R2 resumption, R3+, training, runtime design, RDK-X5, and robot access remain unauthorized. Every next step requires a separate preregistration.
