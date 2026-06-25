# Candidate Trace Analysis

trace: `outputs/analysis/v22_partial_seed_sweep_cpu/v22_partial_61440/seed_001/trace.jsonl`
status: `REVERSE_HEIGHT_COLLAPSE`

## Summary

- samples: `33`
- duration_s: `0.6400`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `-0.0895`
- track_ratio: `-2.2364`
- base_height_min_m: `0.1000`
- body_pitch_p95_rad: `-0.0082`
- reward_mean: `-12.2625`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 4 | 0.0800 |
| `first_low_height` | 31 | 0.6200 |
| `first_done` | 32 | 0.6400 |
| `first_one_foot` | 2 | NA |
| `first_no_contact` | 30 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/forward_wrong_direction` | 696.2212 |
| `cost/forward_shortfall` | 408.8889 |
| `cost/command_progress_shortfall` | 114.6051 |
| `cost/orientation` | 0.0161 |
| `cost/forward_contact_support` | 0.0048 |
| `cost/forward_pitch` | 0.0043 |
| `cost/torques` | 0.0031 |
| `cost/forward_pitch_rate` | 0.0006 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.4072 | 0.2241 | 0.2640 |
| `left_knee` | 0.1720 | 0.0903 | 0.1252 |
| `left_ankle` | 0.2827 | 0.0516 | 0.0528 |
| `right_hip_pitch` | 0.2633 | 0.1038 | 0.1546 |
| `right_knee` | 0.2338 | 0.0460 | 0.0874 |
| `right_ankle` | 0.2838 | 0.1290 | 0.2372 |

## Soft Prior Alignment

- method: `tick_mod_prior_window`
- period: `50`
- mean_abs_error_mean: `0.2734`
- rms_error_mean: `0.3019`

| joint | abs_error_mean | abs_error_p95 |
|---|---:|---:|
| `left_hip_pitch` | 0.3256 | 0.4931 |
| `left_knee` | 0.3740 | 0.4726 |
| `left_ankle` | 0.1851 | 0.2232 |
| `right_hip_pitch` | 0.2933 | 0.4422 |
| `right_knee` | 0.3481 | 0.5122 |
| `right_ankle` | 0.1143 | 0.1724 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 1 |
| `(1, 0)` | 30 |
| `(1, 1)` | 2 |
