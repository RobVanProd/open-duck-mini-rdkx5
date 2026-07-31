# Candidate Trace Analysis

trace: `outputs/analysis/phase2_z0026_seed5_motion_support_repair_seed5_short/ckpt122880/seed_005/trace.jsonl`
status: `REVERSE_HEIGHT_COLLAPSE`

## Summary

- samples: `64`
- duration_s: `1.2600`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `-0.2184`
- track_ratio: `-2.7300`
- base_height_min_m: `0.0806`
- body_pitch_p95_rad: `-0.0802`
- reward_mean: `0.4084`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 10 | 0.2000 |
| `first_low_height` | 62 | 1.2400 |
| `first_done` | 63 | 1.2600 |
| `first_one_foot` | 5 | NA |
| `first_no_contact` | 0 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0287 |
| `cost/torques` | 0.0074 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.3318 | 0.1181 | 0.1306 |
| `left_knee` | 1.7270 | 0.1861 | 0.5459 |
| `left_ankle` | 1.5000 | 0.2019 | 0.3163 |
| `right_hip_pitch` | 1.3592 | 0.1454 | 0.3675 |
| `right_knee` | 1.7437 | 0.2019 | 0.4942 |
| `right_ankle` | 1.3334 | 0.1300 | 0.1583 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 4 |
| `(0, 1)` | 4 |
| `(1, 0)` | 4 |
| `(1, 1)` | 52 |
