# Candidate Trace Analysis

trace: `outputs/analysis/v21_trace_seed1_cpu/trace.jsonl`
status: `REVERSE_HEIGHT_COLLAPSE`

## Summary

- samples: `34`
- duration_s: `0.6600`
- command_x_m_s: `0.0400`
- mean_local_vx_m_s: `-0.0870`
- track_ratio: `-2.1760`
- base_height_min_m: `0.0919`
- body_pitch_p95_rad: `-0.0079`
- reward_mean: `-13.0548`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 0 | 0.0000 |
| `first_low_height` | 32 | 0.6400 |
| `first_done` | 33 | 0.6600 |
| `first_one_foot` | 2 | NA |
| `first_no_contact` | 33 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/forward_wrong_direction` | 675.0524 |
| `cost/forward_shortfall` | 560.8164 |
| `cost/command_progress_shortfall` | 136.6285 |
| `cost/orientation` | 0.0161 |
| `cost/forward_contact_support` | 0.0057 |
| `cost/forward_pitch` | 0.0052 |
| `cost/torques` | 0.0030 |
| `cost/forward_pitch_rate` | 0.0007 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.4246 | 0.2145 | 0.2534 |
| `left_knee` | 0.2414 | 0.0915 | 0.1334 |
| `left_ankle` | 0.3556 | 0.0444 | 0.0448 |
| `right_hip_pitch` | 0.2331 | 0.1028 | 0.1481 |
| `right_knee` | 0.2362 | 0.0413 | 0.0877 |
| `right_ankle` | 0.3633 | 0.1309 | 0.2551 |

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 1 |
| `(1, 0)` | 31 |
| `(1, 1)` | 2 |
