# Candidate Trace Analysis

trace: `outputs/analysis/v21_trace_seed2_cpu/trace.jsonl`
status: `LOW_PROGRESS_TERMINATION`

## Summary

- samples: `70`
- duration_s: `1.3800`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `0.0059`
- track_ratio: `0.1478`
- base_height_min_m: `0.1526`
- body_pitch_p95_rad: `0.0172`
- reward_mean: `-0.1043`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 6 | 0.1200 |
| `first_low_height` | NA | NA |
| `first_done` | 69 | 1.3800 |
| `first_one_foot` | 0 | NA |
| `first_no_contact` | NA | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/forward_shortfall` | 17.2315 |
| `cost/forward_wrong_direction` | 2.9671 |
| `cost/command_progress_failure` | 2.1429 |
| `cost/command_progress_shortfall` | 1.6890 |
| `cost/forward_overshoot` | 0.0056 |
| `cost/torques` | 0.0024 |
| `cost/forward_contact_support` | 0.0001 |
| `cost/forward_pitch_rate` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.2882 | 0.0824 | 0.3025 |
| `left_knee` | 0.5274 | 0.0535 | 0.4884 |
| `left_ankle` | 0.2286 | 0.0201 | 0.0885 |
| `right_hip_pitch` | 0.1869 | 0.0548 | 0.1571 |
| `right_knee` | 0.3385 | 0.0527 | 0.2658 |
| `right_ankle` | 0.3049 | 0.0859 | 0.3267 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 2 |
| `(1, 0)` | 2 |
| `(1, 1)` | 66 |
