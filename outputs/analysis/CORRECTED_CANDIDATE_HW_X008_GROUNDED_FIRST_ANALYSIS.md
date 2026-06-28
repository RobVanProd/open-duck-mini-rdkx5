# Instrumented Low-Command Hardware Eval Analysis

status: `HOLD_TRACKING_P95_OVER_LIMIT`
telemetry: `outputs/first_evidence/20260628T011648Z_corrected_candidate_x008_grounded_first/corrected_candidate_x008_grounded_first.jsonl`

This is offline analysis of existing telemetry. The tool did not SSH, deploy, command motors, or run a policy.

## Summary

- samples: `249`
- target/actual samples: `249`
- max pitch-chain sent velocity p95: `1.8081` rad/s
- max pitch-chain tracking p95: `0.1059` rad
- bus totals: `{'read_errors': 12, 'crc_errors': 0, 'write_errors': 0}`

## Pitch Chain

| joint | sent vel p95 | sent vel max | tracking p95 | tracking max | action sat pct |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.4682 | 2.1442 | 0.1046 | 0.1337 | 0.00 |
| left_knee | 1.8081 | 2.2193 | 0.1059 | 0.1494 | 0.00 |
| left_ankle | 1.3630 | 1.8553 | 0.0824 | 0.1142 | 0.00 |
| right_hip_pitch | 1.3117 | 1.9475 | 0.0815 | 0.1132 | 0.00 |
| right_knee | 1.7199 | 2.3894 | 0.1011 | 0.1432 | 0.00 |
| right_ankle | 1.1218 | 2.2593 | 0.0717 | 0.1395 | 0.00 |

## Interpretation

- `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY` means the telemetry stayed under the configured analysis thresholds; it is not an automatic grounded-walking approval.
- Holds should be reviewed before any further robot motion.
- If the corrected-knee actuator fit has not been refreshed, treat this as descriptive telemetry only.
