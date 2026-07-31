# Ground-Up Torso-COM Reset-Estimator Behavior Decision

status: `PASS_RESET_ESTIMATOR_BEHAVIOR_EVALUATION_NO_ADVANCE`
decision: `CLOSE_RESET_EST_LATCH_U05_NO_PASS`
selected arm: `NONE`
training reward used for selection: `False`

| arm | matrices | cells | endpoint tracking worst | endpoint min vx | nominal tracking worst | pass |
|---|---:|---:|---:|---:|---:|---|
| `RESET_EST_LATCH_U05` | 4/12 | 20/48 | 0.186235136 | -0.386315625 | 0.181910783 | `False` |

Both checkpoints do not pass every frozen cell; the reset-estimator arm is closed without retry or closest-checkpoint promotion.
Training, Colab, runtime design, GPU/iGPU, RDK-X5, and robot access remain unauthorized.
