# Candidate Trace Analysis

trace: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student_x008_gate/live_iter2_ppo_loc/seed_006/trace.jsonl`
status: `REVERSE_HEIGHT_COLLAPSE`

## Summary

- samples: `341`
- duration_s: `6.8000`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `-0.0322`
- track_ratio: `-0.4030`
- base_height_min_m: `0.0731`
- body_pitch_p95_rad: `0.2006`
- reward_mean: `0.4443`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 44 | 0.8800 |
| `first_low_height` | 338 | 6.7600 |
| `first_done` | 340 | 6.8000 |
| `first_one_foot` | 30 | NA |
| `first_no_contact` | 340 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0202 |
| `cost/torques` | 0.0055 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.3832 | 0.1377 | 0.1721 |
| `left_knee` | 1.6050 | 0.1838 | 0.2182 |
| `left_ankle` | 1.3947 | 0.1458 | 0.1679 |
| `right_hip_pitch` | 1.2955 | 0.1227 | 0.1318 |
| `right_knee` | 1.6252 | 0.1767 | 0.2097 |
| `right_ankle` | 1.4226 | 0.1435 | 0.1677 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 1 |
| `(0, 1)` | 24 |
| `(1, 0)` | 27 |
| `(1, 1)` | 289 |
