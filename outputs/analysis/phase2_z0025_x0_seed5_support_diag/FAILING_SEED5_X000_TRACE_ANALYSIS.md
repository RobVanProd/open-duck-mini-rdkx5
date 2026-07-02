# Candidate Trace Analysis

trace: `outputs/analysis/phase2_z0025_x0_seed5_recovery_dagger_iter0/rollouts_x0/student/seed_005/trace.jsonl`
status: `REVERSE_HEIGHT_COLLAPSE`

## Summary

- samples: `43`
- duration_s: `0.8400`
- command_x_m_s: `0.0000`
- mean_local_vx_m_s: `-0.3468`
- track_ratio: `NA`
- base_height_min_m: `0.0575`
- body_pitch_p95_rad: `-0.0553`
- reward_mean: `0.4299`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 8 | 0.1600 |
| `first_low_height` | 39 | 0.7800 |
| `first_done` | 42 | 0.8400 |
| `first_one_foot` | 5 | NA |
| `first_no_contact` | 0 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/stand_still` | 0.8400 |
| `cost/torques` | 0.0046 |
| `cost/action_rate` | 0.0014 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.5828 | 0.0316 | 0.0671 |
| `left_knee` | 0.2750 | 0.2074 | 0.4942 |
| `left_ankle` | 0.5599 | 0.0897 | 0.2069 |
| `right_hip_pitch` | 0.3662 | 0.1441 | 0.2515 |
| `right_knee` | 0.2383 | 0.2106 | 0.5062 |
| `right_ankle` | 0.3740 | 0.1169 | 0.2529 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 2 |
| `(0, 1)` | 2 |
| `(1, 0)` | 2 |
| `(1, 1)` | 37 |
