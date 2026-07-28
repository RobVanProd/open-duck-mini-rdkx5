# T86 rolling-midpoint full R2 result

- Status: `HOLD_T86_ROLLING_MIDPOINT_R2`
- Decision: `STOP_T86_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE`
- Conditions: `4/20`
- Green cells: `63/64`
- First failed condition: `JOINT_FRICTIONLOSS_HI`

| # | condition | green | tracking p95 | min vx | current run | overload run |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `FLOOR_FRICTION_LO` | 16/16 | 0.179007614 | 0.047410238 | 12 | 12 |
| 2 | `FLOOR_FRICTION_HI` | 16/16 | 0.179007614 | 0.047410238 | 12 | 12 |
| 3 | `JOINT_FRICTIONLOSS_LO` | 16/16 | 0.179146528 | 0.047997284 | 15 | 15 |
| 4 | `JOINT_FRICTIONLOSS_HI` | 15/16 | 0.178220052 | 0.047566176 | 13 | 13 |

Conditions ran in frozen order and stopped after the first complete failed condition. Raw traces remain on D:.

A pass authorizes only deployment-readiness package preregistration. Gate 5 hardware, RDK-X5, robot access, torque, motion, and deployment remain closed.
