# Ground-Up Torso-COM Reset-Estimator Behavior Decision

status: `FAIL_RESET_ESTIMATOR_BEHAVIOR_EVIDENCE_CONTRACT`
decision: `INVALID_EVIDENCE`
selected arm: `NONE`
training reward used for selection: `False`

This initial report has no selection authority. Its sole failed check was a
literal preregistration-text matcher that did not accept the line-wrapped
phrase "both full-range checkpoints must pass every cell." Raw matrix evidence
and all metric gates were unchanged. The corrected aggregation is recorded in
`GROUND_UP_TORSO_COM_RESET_ESTIMATOR_BEHAVIOR_DECISION_20260715.md`.

| arm | matrices | cells | endpoint tracking worst | endpoint min vx | nominal tracking worst | pass |
|---|---:|---:|---:|---:|---:|---|
| `RESET_EST_LATCH_U05` | 4/12 | 20/48 | 0.186235136 | -0.386315625 | 0.181910783 | `False` |

Both checkpoints do not pass every frozen cell; the reset-estimator arm is closed without retry or closest-checkpoint promotion.
Training, Colab, runtime design, GPU/iGPU, RDK-X5, and robot access remain unauthorized.
