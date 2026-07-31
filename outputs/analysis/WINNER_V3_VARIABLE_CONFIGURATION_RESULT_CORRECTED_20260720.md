# Winner-v3 Variable-Configuration Corrected Result

status: `HOLD_WINNER_V3_VARIABLE_CONFIGURATION_RESULT_REPORTING_CORRECTED`

decision: `HOLD_WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT`

Cells: `48/1024` pass after removing only the false CPU display-name failure.

| checkpoint | cells | passing | all pass | worst tracking p95 | worst current p95 | minimum moving vx |
|---:|---:|---:|---|---:|---:|---:|
| 1003520 | 512 | 24 | `False` | 0.206845775 | 3.374259928 | -0.389848125 |
| 2007040 | 512 | 24 | `False` | 0.198633032 | 3.612190809 | -0.408615665 |

## Physical failure counts

- `bilateral_transitions`: `1`
- `candidate_gate_pass`: `251`
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

The raw aggregate is preserved. Its `INVALID` token came from two reporting defects: JAX exposed `TFRT_CPU_0` instead of a display string containing `CpuDevice`, and the aggregate treated every expected early-termination trace as missing evidence. All 1,024 trace hashes, row/sample counts, schemas, finite-value audits, reset audits and per-run readbacks validate. Duration and trace-contract failures remain behavioral failures in the corrected result.

Both persistent checkpoints fail the frozen all-512 rule. No graph, closest configuration, reward, or sibling checkpoint is promoted. Robot clearance and runtime adoption remain `NO`.
