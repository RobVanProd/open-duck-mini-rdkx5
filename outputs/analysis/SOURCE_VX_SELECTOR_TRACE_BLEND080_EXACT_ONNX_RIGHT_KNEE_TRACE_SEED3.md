# Candidate Trace Analysis

trace: `outputs/analysis/source_vx_selector_trace_blend080_exact_onnx_right_knee_trace_seed3/trace.jsonl`
status: `UNKNOWN`

## Summary

- samples: `500`
- duration_s: `9.9800`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `0.0404`
- track_ratio: `0.5050`
- base_height_min_m: `0.1549`
- body_pitch_p95_rad: `0.0973`
- reward_mean: `0.4587`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 0 | 0.0000 |
| `first_low_height` | NA | NA |
| `first_done` | NA | NA |
| `first_one_foot` | 5 | NA |
| `first_no_contact` | 3 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0501 |
| `cost/torques` | 0.0079 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 2.0496 | 0.1518 | 0.1680 |
| `left_knee` | 2.8390 | 0.2090 | 0.2342 |
| `left_ankle` | 2.8036 | 0.2076 | 0.2713 |
| `right_hip_pitch` | 1.6291 | 0.1443 | 0.1511 |
| `right_knee` | 5.1130 | 0.2756 | 0.2990 |
| `right_ankle` | 2.8797 | 0.1994 | 0.2948 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 2 |
| `(0, 1)` | 116 |
| `(1, 0)` | 90 |
| `(1, 1)` | 292 |
