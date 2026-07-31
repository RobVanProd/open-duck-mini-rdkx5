# Candidate Trace Analysis

trace: `outputs/analysis/phase2_rate160_z0075_intermediate_push_seed5_trace/phase_mod_rate160/seed_005/trace.jsonl`
status: `UNKNOWN`

## Summary

- samples: `750`
- duration_s: `14.9800`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `0.0282`
- track_ratio: `0.3530`
- base_height_min_m: `0.1577`
- body_pitch_p95_rad: `0.1777`
- reward_mean: `0.4604`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 44 | 0.8800 |
| `first_low_height` | NA | NA |
| `first_done` | NA | NA |
| `first_one_foot` | 28 | NA |
| `first_no_contact` | NA | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0218 |
| `cost/torques` | 0.0055 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.3777 | 0.1395 | 0.1784 |
| `left_knee` | 1.6503 | 0.1878 | 0.2303 |
| `left_ankle` | 1.3957 | 0.1459 | 0.1748 |
| `right_hip_pitch` | 1.4423 | 0.1240 | 0.1468 |
| `right_knee` | 1.6268 | 0.1763 | 0.2127 |
| `right_ankle` | 1.4133 | 0.1503 | 0.1845 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 55 |
| `(1, 0)` | 120 |
| `(1, 1)` | 575 |
