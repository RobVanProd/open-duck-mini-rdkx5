# Candidate Trace Analysis

trace: `outputs/analysis/phase2_z0025_x0_seed5_recovery_dagger_iter0/rollouts_x008/student/seed_005/trace.jsonl`
status: `UNKNOWN`

## Summary

- samples: `100`
- duration_s: `1.9800`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `0.0401`
- track_ratio: `0.5011`
- base_height_min_m: `0.1464`
- body_pitch_p95_rad: `0.1201`
- reward_mean: `0.4398`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 11 | 0.2200 |
| `first_low_height` | NA | NA |
| `first_done` | NA | NA |
| `first_one_foot` | 5 | NA |
| `first_no_contact` | 0 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0253 |
| `cost/torques` | 0.0068 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.4762 | 0.1430 | 0.1612 |
| `left_knee` | 1.8623 | 0.2003 | 0.4970 |
| `left_ankle` | 1.7019 | 0.1641 | 0.2865 |
| `right_hip_pitch` | 1.5268 | 0.1294 | 0.3067 |
| `right_knee` | 1.9072 | 0.1783 | 0.4827 |
| `right_ankle` | 1.7025 | 0.1579 | 0.1921 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 2 |
| `(0, 1)` | 3 |
| `(1, 0)` | 3 |
| `(1, 1)` | 92 |
