# Candidate Trace Analysis

trace: `outputs/analysis/v22_partial_seed_sweep_cpu/v22_partial_61440/seed_002/trace.jsonl`
status: `LOW_PROGRESS_TERMINATION`

## Summary

- samples: `70`
- duration_s: `1.3800`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `0.0036`
- track_ratio: `0.0889`
- base_height_min_m: `0.1526`
- body_pitch_p95_rad: `0.0059`
- reward_mean: `-0.1068`
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
| `cost/forward_shortfall` | 11.1184 |
| `cost/forward_wrong_direction` | 2.5005 |
| `cost/command_progress_failure` | 2.1429 |
| `cost/command_progress_shortfall` | 1.9867 |
| `cost/forward_overshoot` | 0.0057 |
| `cost/torques` | 0.0024 |
| `cost/forward_contact_support` | 0.0001 |
| `cost/forward_pitch_rate` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.3712 | 0.0805 | 0.2974 |
| `left_knee` | 0.3498 | 0.0561 | 0.4998 |
| `left_ankle` | 0.3612 | 0.0212 | 0.0782 |
| `right_hip_pitch` | 0.3075 | 0.0566 | 0.1529 |
| `right_knee` | 0.2988 | 0.0542 | 0.2832 |
| `right_ankle` | 0.3287 | 0.0913 | 0.3511 |

## Soft Prior Alignment

- method: `tick_mod_prior_window`
- period: `50`
- mean_abs_error_mean: `0.2685`
- rms_error_mean: `0.2929`

| joint | abs_error_mean | abs_error_p95 |
|---|---:|---:|
| `left_hip_pitch` | 0.2799 | 0.4414 |
| `left_knee` | 0.3560 | 0.4781 |
| `left_ankle` | 0.1457 | 0.1778 |
| `right_hip_pitch` | 0.3327 | 0.4599 |
| `right_knee` | 0.3457 | 0.4849 |
| `right_ankle` | 0.1509 | 0.1822 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 2 |
| `(1, 0)` | 3 |
| `(1, 1)` | 65 |
