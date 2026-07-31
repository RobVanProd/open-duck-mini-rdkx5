# Candidate Trace Analysis

trace: `/tmp/open_duck_v24_corrected_seed0_trace/trace.jsonl`
status: `LOW_PROGRESS_TERMINATION`

## Summary

- samples: `70`
- duration_s: `1.3800`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `-0.0008`
- track_ratio: `-0.0194`
- base_height_min_m: `0.1537`
- body_pitch_p95_rad: `0.0248`
- reward_mean: `-0.5903`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 0 | 0.0000 |
| `first_low_height` | NA | NA |
| `first_done` | 69 | 1.3800 |
| `first_one_foot` | 0 | NA |
| `first_no_contact` | NA | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/forward_shortfall` | 20.0408 |
| `cost/forward_wrong_direction` | 9.4851 |
| `cost/command_progress_shortfall` | 6.7829 |
| `cost/command_progress_failure` | 2.1429 |
| `cost/forward_double_support` | 0.4643 |
| `cost/torques` | 0.0021 |
| `cost/forward_overshoot` | 0.0003 |
| `cost/base_height` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.3342 | 0.0636 | 0.2869 |
| `left_knee` | 0.1435 | 0.0602 | 0.4895 |
| `left_ankle` | 0.2391 | 0.0324 | 0.1976 |
| `right_hip_pitch` | 0.3704 | 0.0280 | 0.0907 |
| `right_knee` | 0.3653 | 0.0535 | 0.0678 |
| `right_ankle` | 0.2426 | 0.0663 | 0.2937 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 5 |
| `(1, 1)` | 65 |
