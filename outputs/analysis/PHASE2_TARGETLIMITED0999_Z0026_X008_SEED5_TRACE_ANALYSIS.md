# Candidate Trace Analysis

trace: `outputs/analysis/phase2_targetlimited0999_z0026_x008_seed5_trace_short/limited/seed_005/trace.jsonl`
status: `REVERSE_HEIGHT_COLLAPSE`

## Summary

- samples: `57`
- duration_s: `1.1200`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `-0.2573`
- track_ratio: `-3.2164`
- base_height_min_m: `0.0710`
- body_pitch_p95_rad: `-0.0673`
- reward_mean: `0.4030`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 10 | 0.2000 |
| `first_low_height` | 54 | 1.0800 |
| `first_done` | 56 | 1.1200 |
| `first_one_foot` | 5 | NA |
| `first_no_contact` | 0 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0217 |
| `cost/torques` | 0.0070 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.4853 | 0.1275 | 0.1587 |
| `left_knee` | 1.8320 | 0.1874 | 0.4970 |
| `left_ankle` | 1.5127 | 0.1563 | 0.2684 |
| `right_hip_pitch` | 1.1904 | 0.1858 | 0.3067 |
| `right_knee` | 1.2474 | 0.1738 | 0.4827 |
| `right_ankle` | 1.5028 | 0.1452 | 0.1924 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 5 |
| `(0, 1)` | 2 |
| `(1, 0)` | 4 |
| `(1, 1)` | 46 |
