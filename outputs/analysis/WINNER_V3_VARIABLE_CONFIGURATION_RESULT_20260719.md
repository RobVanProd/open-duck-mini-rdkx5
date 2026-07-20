# Winner-v3 Variable-Configuration Result

status: `INVALID_WINNER_V3_VARIABLE_CONFIGURATION_RESULT`
decision: `INVALID_WINNER_V3_VARIABLE_CONFIGURATION_STUDY`

Cells: `0/1024` pass.

| checkpoint | cells | passing | all pass | worst tracking p95 | worst current p95 | minimum moving vx |
|---:|---:|---:|---|---:|---:|---:|
| 1003520 | 512 | 0 | `False` | 0.206845775 | 3.374259928 | -0.389848125 |
| 2007040 | 512 | 0 | `False` | 0.198633032 | 3.612190809 | -0.408615665 |

## Failure counts

- `bilateral_transitions`: `1`
- `candidate_gate_pass`: `251`
- `cpu_only`: `1024`
- `current_p95_at_most_0p65`: `944`
- `duration_complete_600`: `239`
- `positive_command_consistent_motion`: `107`
- `trace_contract`: `239`
- `tracking_p95_at_most_0p20`: `4`
- `zero_command_base_height`: `36`
- `zero_command_velocity`: `36`
- `zero_envelope_excess`: `34`
- `zero_rate_excess`: `12`
- `zero_saturation`: `38`

Both persistent checkpoints must pass all 512 cells. No sibling, closest configuration, aggregate score, training reward, or simulator reward can promote a failure.

This CPU result does not itself authorize RDK-X5/robot access, runtime adoption, Gate 5, torque, motion, or deployment.
