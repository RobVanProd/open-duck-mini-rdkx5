# Instrumented Low-Command Hardware Eval Analysis

status: `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY`
telemetry: `outputs/first_evidence/20260628T012023Z_corrected_candidate_x008_grounded_second_surface/corrected_candidate_x008_grounded_second_surface.jsonl`

This is offline analysis of existing telemetry. The tool did not SSH, deploy, command motors, or run a policy.

## Summary

- samples: `249`
- target/actual samples: `249`
- max pitch-chain sent velocity p95: `1.1698` rad/s
- max pitch-chain tracking p95: `0.0711` rad
- bus totals: `{'read_errors': 6, 'crc_errors': 0, 'write_errors': 0}`

## Pitch Chain

| joint | sent vel p95 | sent vel max | tracking p95 | tracking max | action sat pct |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.7368 | 1.3547 | 0.0574 | 0.1190 | 0.00 |
| left_knee | 1.1698 | 1.6355 | 0.0711 | 0.1326 | 0.00 |
| left_ankle | 0.9093 | 1.3553 | 0.0619 | 0.0869 | 0.00 |
| right_hip_pitch | 0.6099 | 1.3182 | 0.0397 | 0.1096 | 0.00 |
| right_knee | 0.8262 | 1.9568 | 0.0533 | 0.0801 | 0.00 |
| right_ankle | 0.6124 | 1.6118 | 0.0444 | 0.1061 | 0.00 |

## Interpretation

- `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY` means the telemetry stayed under the configured analysis thresholds; it is not an automatic grounded-walking approval.
- Holds should be reviewed before any further robot motion.
- If the corrected-knee actuator fit has not been refreshed, treat this as descriptive telemetry only.
