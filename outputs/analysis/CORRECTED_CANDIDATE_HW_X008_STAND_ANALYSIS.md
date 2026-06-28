# Instrumented Low-Command Hardware Eval Analysis

status: `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY`
telemetry: `outputs/first_evidence/20260628T010517Z_corrected_candidate_x008_stand/corrected_candidate_x008_stand.jsonl`

This is offline analysis of existing telemetry. The tool did not SSH, deploy, command motors, or run a policy.

## Summary

- samples: `747`
- target/actual samples: `747`
- max pitch-chain sent velocity p95: `0.4065` rad/s
- max pitch-chain tracking p95: `0.0222` rad
- bus totals: `{'read_errors': 6, 'crc_errors': 0, 'write_errors': 0}`

## Pitch Chain

| joint | sent vel p95 | sent vel max | tracking p95 | tracking max | action sat pct |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.3929 | 0.7560 | 0.0212 | 0.1105 | 0.00 |
| left_knee | 0.2862 | 0.7964 | 0.0192 | 0.0495 | 0.00 |
| left_ankle | 0.4065 | 1.3292 | 0.0222 | 0.0963 | 0.00 |
| right_hip_pitch | 0.3449 | 0.8072 | 0.0214 | 0.1104 | 0.00 |
| right_knee | 0.2040 | 0.5594 | 0.0159 | 0.0406 | 0.00 |
| right_ankle | 0.2237 | 0.5226 | 0.0125 | 0.1035 | 0.00 |

## Interpretation

- `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY` means the telemetry stayed under the configured analysis thresholds; it is not an automatic grounded-walking approval.
- Holds should be reviewed before any further robot motion.
- If the corrected-knee actuator fit has not been refreshed, treat this as descriptive telemetry only.
