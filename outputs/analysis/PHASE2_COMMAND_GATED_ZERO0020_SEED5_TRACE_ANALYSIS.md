# Candidate Trace Analysis

trace: `outputs/analysis/phase2_command_gated_zero0020_seed5_failure_trace/command_gated_zero0020/seed_005/trace.jsonl`
status: `HEIGHT_COLLAPSE`

## Summary

- samples: `158`
- duration_s: `3.1400`
- command_x_m_s: `0.0800`
- mean_local_vx_m_s: `0.1367`
- track_ratio: `1.7083`
- base_height_min_m: `-0.0058`
- body_pitch_p95_rad: `0.8743`
- reward_mean: `0.4439`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 45 | 0.9000 |
| `first_low_height` | 150 | 3.0000 |
| `first_done` | 157 | 3.1400 |
| `first_one_foot` | 32 | NA |
| `first_no_contact` | 153 | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/action_rate` | 0.0202 |
| `cost/torques` | 0.0060 |
| `cost/stand_still` | 0.0000 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 1.2307 | 0.1410 | 0.1678 |
| `left_knee` | 1.5591 | 0.1977 | 0.2257 |
| `left_ankle` | 1.3800 | 0.1502 | 0.1681 |
| `right_hip_pitch` | 1.3696 | 0.1218 | 0.1307 |
| `right_knee` | 1.5931 | 0.1844 | 0.2123 |
| `right_ankle` | 1.4800 | 0.1513 | 0.1741 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 0)` | 3 |
| `(0, 1)` | 3 |
| `(1, 0)` | 12 |
| `(1, 1)` | 140 |
