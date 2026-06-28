# Instrumented Low-Command Hardware Eval Analysis

status: `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY`
telemetry: `outputs/first_evidence/20260628T010359Z_corrected_candidate_x0_stand/corrected_candidate_x0_stand.jsonl`

This is offline analysis of existing telemetry. The tool did not SSH, deploy, command motors, or run a policy.

## Summary

- samples: `747`
- target/actual samples: `747`
- max pitch-chain sent velocity p95: `0.2310` rad/s
- max pitch-chain tracking p95: `0.0145` rad
- bus totals: `{'read_errors': 18, 'crc_errors': 0, 'write_errors': 0}`

## Pitch Chain

| joint | sent vel p95 | sent vel max | tracking p95 | tracking max | action sat pct |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.2008 | 0.4152 | 0.0130 | 0.1006 | 0.00 |
| left_knee | 0.2108 | 0.6519 | 0.0145 | 0.0385 | 0.00 |
| left_ankle | 0.2310 | 0.8140 | 0.0141 | 0.0960 | 0.00 |
| right_hip_pitch | 0.1677 | 0.6054 | 0.0129 | 0.1071 | 0.00 |
| right_knee | 0.1866 | 0.5421 | 0.0141 | 0.0422 | 0.00 |
| right_ankle | 0.1807 | 0.3192 | 0.0120 | 0.0955 | 0.00 |

## Interpretation

- `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY` means the telemetry stayed under the configured analysis thresholds; it is not an automatic grounded-walking approval.
- Holds should be reviewed before any further robot motion.
- If the corrected-knee actuator fit has not been refreshed, treat this as descriptive telemetry only.
