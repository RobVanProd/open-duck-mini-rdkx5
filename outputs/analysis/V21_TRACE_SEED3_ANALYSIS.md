# Candidate Trace Analysis

trace: `outputs/analysis/v21_trace_seed3_cpu/trace.jsonl`
status: `LOW_PROGRESS_TERMINATION`

## Summary

- samples: `70`
- duration_s: `1.3800`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `-0.0172`
- track_ratio: `-0.4312`
- base_height_min_m: `0.1589`
- body_pitch_p95_rad: `0.0821`
- reward_mean: `-4.8066`
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
| `cost/forward_shortfall` | 94.6439 |
| `cost/command_progress_shortfall` | 83.3511 |
| `cost/forward_wrong_direction` | 82.3907 |
| `cost/command_progress_failure` | 2.1429 |
| `cost/forward_contact_support` | 0.0070 |
| `cost/torques` | 0.0017 |
| `cost/forward_pitch_rate` | 0.0001 |
| `cost/orientation` | 0.0001 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.2054 | 0.0381 | 0.1546 |
| `left_knee` | 0.6720 | 0.1035 | 0.1255 |
| `left_ankle` | 0.3013 | 0.0407 | 0.2301 |
| `right_hip_pitch` | 0.4831 | 0.0330 | 0.1504 |
| `right_knee` | 0.1814 | 0.0607 | 0.1675 |
| `right_ankle` | 0.2757 | 0.0485 | 0.2538 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 4 |
| `(1, 0)` | 5 |
| `(1, 1)` | 61 |
