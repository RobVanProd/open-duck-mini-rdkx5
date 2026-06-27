# Candidate Trace Analysis

trace: `outputs/analysis/v21_trace_seed0_cpu/trace.jsonl`
status: `LOW_PROGRESS_TERMINATION`

## Summary

- samples: `70`
- duration_s: `1.3800`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `-0.0011`
- track_ratio: `-0.0269`
- base_height_min_m: `0.1536`
- body_pitch_p95_rad: `0.0551`
- reward_mean: `-0.9114`
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
| `cost/forward_shortfall` | 33.1709 |
| `cost/forward_wrong_direction` | 13.6012 |
| `cost/command_progress_shortfall` | 8.4740 |
| `cost/command_progress_failure` | 2.1429 |
| `cost/torques` | 0.0021 |
| `cost/forward_contact_support` | 0.0001 |
| `cost/forward_pitch_rate` | 0.0001 |
| `cost/base_height` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.1877 | 0.0563 | 0.2932 |
| `left_knee` | 0.2223 | 0.0652 | 0.4834 |
| `left_ankle` | 0.1863 | 0.0427 | 0.1870 |
| `right_hip_pitch` | 0.2009 | 0.0280 | 0.0839 |
| `right_knee` | 0.4125 | 0.0628 | 0.0665 |
| `right_ankle` | 0.1749 | 0.0647 | 0.3077 |

## Soft Prior Alignment

- method: `tick_mod_prior_window`
- period: `50`
- mean_abs_error_mean: `0.2614`
- rms_error_mean: `0.2887`

| joint | abs_error_mean | abs_error_p95 |
|---|---:|---:|
| `left_hip_pitch` | 0.2777 | 0.4361 |
| `left_knee` | 0.3457 | 0.4597 |
| `left_ankle` | 0.1394 | 0.1822 |
| `right_hip_pitch` | 0.3387 | 0.4642 |
| `right_knee` | 0.3347 | 0.4753 |
| `right_ankle` | 0.1324 | 0.1598 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 3 |
| `(1, 1)` | 67 |
