# T53 uniform half-head R2 remainder result

- Status: `HOLD_T53_UNIFORM_HALF_HEAD_R2_REMAINDER`
- Decision: `STOP_T53_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE`
- Conditions: `3/16`
- Green cells: `40/48`
- First failed condition: `TORSO_COM_X_NEG`

| # | condition | green | tracking p95 | min vx | current run | overload run |
|---:|---|---:|---:|---:|---:|---:|
| 5 | `ARMATURE_LO` | 16/16 | 0.171842223 | 0.052609381 | 15 | 15 |
| 6 | `ARMATURE_HI` | 16/16 | 0.173728710 | 0.051970581 | 15 | 15 |
| 7 | `TORSO_COM_X_NEG` | 8/16 | 0.168516642 | -0.060899324 | 6 | 6 |

Conditions ran in frozen order and stopped after the first complete failed condition. Raw traces remain on D:.

A pass authorizes only Gate 5 deployment-package preregistration. Hardware, RDK-X5, robot access, torque, motion, and deployment remain closed.
