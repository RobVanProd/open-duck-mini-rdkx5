# Candidate Trace Analysis

trace: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_failure_trace/phase2_z0075_iter3_seed0_recovery_rate150/seed_000/trace.jsonl`
status: `HEIGHT_COLLAPSE`

## Summary

- samples: `126`
- duration_s: `2.5000`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `0.1657`
- track_ratio: `2.0714`
- base_height_min_m: `0.0037`
- body_pitch_p95_rad: `1.0009`
- reward_mean: `0.4401`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 0 | 0.0000 |
| `first_low_height` | 118 | 2.3600 |
| `first_done` | 125 | 2.5000 |
| `first_one_foot` | 29 | NA |
| `first_no_contact` | NA | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0249 |
| `cost/torques` | 0.0063 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.3356 | 0.1342 | 0.1697 |
| `left_knee` | 1.8415 | 0.2017 | 0.2280 |
| `left_ankle` | 1.6595 | 0.1573 | 0.1788 |
| `right_hip_pitch` | 1.3540 | 0.1277 | 0.1366 |
| `right_knee` | 1.7697 | 0.1902 | 0.2144 |
| `right_ankle` | 1.4457 | 0.1485 | 0.1634 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 5 |
| `(1, 0)` | 14 |
| `(1, 1)` | 107 |
