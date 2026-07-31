# T41 uniform-normalizer R2 result

- Status: `HOLD_T41_UNIFORM_NORMALIZER_R2`
- Decision: `STOP_T41_AT_FIRST_FAILED_R2_CONDITION_AND_ATTRIBUTE`
- Conditions: `3/20`
- Green cells: `47/48`
- First failed condition: `JOINT_FRICTIONLOSS_LO`

| # | condition | green | tracking p95 | min vx | current run | overload run |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `FLOOR_FRICTION_LO` | 16/16 | 0.169115901 | 0.043205272 | 14 | 15 |
| 2 | `FLOOR_FRICTION_HI` | 16/16 | 0.169115901 | 0.043205272 | 14 | 15 |
| 3 | `JOINT_FRICTIONLOSS_LO` | 15/16 | 0.170190978 | 0.043430225 | 14 | 15 |

Conditions ran in frozen order and stopped after the first complete failed condition. Raw traces remain on D:.

Gate 5 hardware, RDK-X5, robot access, torque, motion, and deployment remain closed.
