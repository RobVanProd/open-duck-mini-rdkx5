# Candidate Trace Analysis

trace: `outputs/analysis/v22_partial_seed_sweep_cpu/v22_partial_61440/seed_003/trace.jsonl`
status: `LOW_PROGRESS_TERMINATION`

## Summary

- samples: `70`
- duration_s: `1.3800`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `-0.0182`
- track_ratio: `-0.4547`
- base_height_min_m: `0.1588`
- body_pitch_p95_rad: `0.0691`
- reward_mean: `-4.1867`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 0 | 0.0000 |
| `first_low_height` | NA | NA |
| `first_done` | 69 | 1.3800 |
| `first_one_foot` | 2 | NA |
| `first_no_contact` | 3 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/forward_wrong_direction` | 81.6103 |
| `cost/command_progress_shortfall` | 70.5304 |
| `cost/forward_shortfall` | 64.9621 |
| `cost/command_progress_failure` | 2.1429 |
| `cost/forward_contact_support` | 0.0059 |
| `cost/torques` | 0.0017 |
| `cost/forward_pitch_rate` | 0.0001 |
| `cost/orientation` | 0.0001 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.2157 | 0.0359 | 0.1533 |
| `left_knee` | 0.5581 | 0.1026 | 0.1299 |
| `left_ankle` | 0.2054 | 0.0414 | 0.2127 |
| `right_hip_pitch` | 0.4662 | 0.0319 | 0.1540 |
| `right_knee` | 0.2115 | 0.0572 | 0.1644 |
| `right_ankle` | 0.2364 | 0.0462 | 0.2386 |

## Soft Prior Alignment

- method: `tick_mod_prior_window`
- period: `50`
- mean_abs_error_mean: `0.2711`
- rms_error_mean: `0.2971`

| joint | abs_error_mean | abs_error_p95 |
|---|---:|---:|
| `left_hip_pitch` | 0.2818 | 0.4414 |
| `left_knee` | 0.3594 | 0.4803 |
| `left_ankle` | 0.1570 | 0.2190 |
| `right_hip_pitch` | 0.3306 | 0.4713 |
| `right_knee` | 0.3567 | 0.4920 |
| `right_ankle` | 0.1414 | 0.1732 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 4 |
| `(1, 0)` | 5 |
| `(1, 1)` | 61 |
