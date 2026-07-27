# T27 T23 sequential R2 robustness result

- Status: `HOLD_T27_T23_R2_ROBUSTNESS`
- Decision: `STOP_T23_AT_FIRST_FAILED_R2_CONDITION`
- Completed conditions: `1/20`
- Green cells: `10/16`
- First failed condition: `FLOOR_FRICTION_LO`

| # | condition | green | tracking p95 | min vx | current run | overload run |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `FLOOR_FRICTION_LO` | 10/16 | 0.166789985 | 0.044552425 | 14 | 14 |

Conditions run in the frozen order and stop after the first complete failed 16-cell condition. Raw traces remain in the D: evidence cache and are not committed.

This CPU-only result does not authorize Gate 5, RDK-X5 access, robot access, torque, motion, or deployment.
