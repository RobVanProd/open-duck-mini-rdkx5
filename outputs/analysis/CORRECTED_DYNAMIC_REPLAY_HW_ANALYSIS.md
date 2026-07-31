# Instrumented Low-Command Hardware Eval Analysis

status: `HOLD_TARGET_VELOCITY_OVER_LIMIT`
telemetry: `outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl`

This is offline analysis of existing telemetry. The tool did not SSH, deploy, command motors, or run a policy.

## Summary

- samples: `747`
- target/actual samples: `747`
- max pitch-chain sent velocity p95: `5.2168` rad/s
- max pitch-chain tracking p95: `0.2038` rad
- bus totals: `{'read_errors': 9702, 'crc_errors': 0, 'write_errors': 0}`

## Pitch Chain

| joint | sent vel p95 | sent vel max | tracking p95 | tracking max | action sat pct |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | 5.2168 | 5.2256 | 0.1803 | 0.2980 | 0.00 |
| left_knee | 3.6806 | 5.2170 | 0.1963 | 0.2811 | 0.00 |
| left_ankle | 3.8971 | 5.2182 | 0.1476 | 0.2358 | 0.00 |
| right_hip_pitch | 3.2908 | 5.1229 | 0.1516 | 0.2054 | 2.41 |
| right_knee | 4.5150 | 5.2182 | 0.2038 | 0.2548 | 0.00 |
| right_ankle | 3.5479 | 5.2178 | 0.1429 | 0.1893 | 0.00 |

## Interpretation

- `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY` means the telemetry stayed under the configured analysis thresholds; it is not an automatic grounded-walking approval.
- Holds should be reviewed before any further robot motion.
- If the corrected-knee actuator fit has not been refreshed, treat this as descriptive telemetry only.
