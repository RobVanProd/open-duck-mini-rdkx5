# Candidate Trace Analysis

trace: `outputs/analysis/v22_partial_seed_sweep_cpu/v22_partial_61440/seed_000/trace.jsonl`
status: `LOW_PROGRESS_TERMINATION`

## Summary

- samples: `70`
- duration_s: `1.3800`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `-0.0018`
- track_ratio: `-0.0450`
- base_height_min_m: `0.1537`
- body_pitch_p95_rad: `0.0160`
- reward_mean: `-0.6366`
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
| `cost/forward_shortfall` | 18.4214 |
| `cost/forward_wrong_direction` | 10.5282 |
| `cost/command_progress_shortfall` | 8.5002 |
| `cost/command_progress_failure` | 2.1429 |
| `cost/torques` | 0.0020 |
| `cost/forward_contact_support` | 0.0001 |
| `cost/base_height` | 0.0000 |
| `cost/forward_overshoot` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.2750 | 0.0649 | 0.2887 |
| `left_knee` | 0.1301 | 0.0604 | 0.4904 |
| `left_ankle` | 0.2208 | 0.0329 | 0.2011 |
| `right_hip_pitch` | 0.2438 | 0.0265 | 0.0881 |
| `right_knee` | 0.3195 | 0.0514 | 0.0719 |
| `right_ankle` | 0.2041 | 0.0667 | 0.2904 |

## Soft Prior Alignment

- method: `tick_mod_prior_window`
- period: `50`
- mean_abs_error_mean: `0.2712`
- rms_error_mean: `0.2959`

| joint | abs_error_mean | abs_error_p95 |
|---|---:|---:|
| `left_hip_pitch` | 0.2837 | 0.4408 |
| `left_knee` | 0.3625 | 0.4802 |
| `left_ankle` | 0.1546 | 0.1898 |
| `right_hip_pitch` | 0.3319 | 0.4576 |
| `right_knee` | 0.3439 | 0.4858 |
| `right_ankle` | 0.1506 | 0.1747 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 4 |
| `(1, 1)` | 66 |
