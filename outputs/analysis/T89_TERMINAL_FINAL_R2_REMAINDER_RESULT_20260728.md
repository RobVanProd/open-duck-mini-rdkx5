# T89 terminal-final R2 remainder result

- Status: `HOLD_T89_TERMINAL_FINAL_R2_REMAINDER`
- Decision: `STOP_T89_AT_FIRST_TERMINAL_FINAL_FAILURE_AND_ATTRIBUTE`
- New conditions: `2/16`
- Combined cells: `47/48`
- First failed condition: `ARMATURE_HI`

| # | condition | green | tracking p95 | min vx |
|---:|---|---:|---:|---:|
| 5 | `ARMATURE_LO` | 8/8 | 0.179007614 | 0.050670100 |
| 6 | `ARMATURE_HI` | 7/8 | 0.178837800 | 0.048575488 |

This is a single-checkpoint diagnostic and cannot satisfy the two-export persistence gate or authorize deployment.

Training, Gate 5, RDK-X5, robot, torque, and motion remain closed.
