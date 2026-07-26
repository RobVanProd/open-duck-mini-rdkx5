# T9 command-aware x=0 prefix-bypass result

- Status: `PASS_T9_COMMAND_AWARE_PREFIX_BYPASS`
- Decision: `EARN_RESPONSE_CONDITIONED_V121_CONTINUATION_CPU_CONTRACT`
- New x=0 cells: `4/4`
- Combined cells: `16/16`
- Result SHA-256: `57472d927f0896642e5c84351f6238486e656f76aaff73c0aa6ae8607c87ebec`

| checkpoint | fit | green | tracking p95 | rate excess | overcurrent run | overload run |
|---|---|---:|---:|---:|---:|---:|
| `V121_TRAIN_MATCHED_HALF` | `p30` | `True` | 0.030257880687713623 | 0.0 | 0 | 0 |
| `V121_TRAIN_MATCHED_HALF` | `p31_34` | `True` | 0.030257880687713623 | 0.0 | 0 | 0 |
| `V121_TRAIN_MATCHED_FINAL` | `p30` | `True` | 0.030257880687713623 | 0.0 | 0 | 0 |
| `V121_TRAIN_MATCHED_FINAL` | `p31_34` | `True` | 0.030257880687713623 | 0.0 | 0 | 0 |

T9 changes only startup orchestration: paused/x=0 begins directly from home with immutable zero context and no response excitation. The V121 graph, exact-zero deadband, action/history/applied-target semantics, dynamics, and gates are unchanged. The twelve audited T8 moving cells are reused without rerunning.

A pass earns only the separately preregistered response-conditioned continuation CPU software contract. It does not authorize hosted training, robot/RDK-X5 access, Gate 5, torque, motion, deployment, or grounded replay.
