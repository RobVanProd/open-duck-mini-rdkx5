# Candidate Trace Analysis

trace: `outputs/analysis/phase2_z0025_x0_seed5_support_diag/baseline_seed0_x000/parent_z0025_contactphase_rate1p9/seed_000/trace.jsonl`
status: `UNKNOWN`

## Summary

- samples: `100`
- duration_s: `1.9800`
- command_x_m_s: `0.0000`
- mean_local_vx_m_s: `-0.0015`
- track_ratio: `NA`
- base_height_min_m: `0.1520`
- body_pitch_p95_rad: `0.0023`
- reward_mean: `0.5412`
- action_saturation_pct: `0.0000`

## Events

| event | tick | time_s |
|---|---:|---:|
| `first_reverse` | 0 | 0.0000 |
| `first_low_height` | NA | NA |
| `first_done` | NA | NA |
| `first_one_foot` | 0 | NA |
| `first_no_contact` | NA | NA |

## Dominant Cost Means

| term | mean |
|---|---:|
| `cost/stand_still` | 0.3197 |
| `cost/torques` | 0.0019 |
| `cost/action_rate` | 0.0003 |

## Pitch Chain

| joint | target_vel_p95_rad_s | tracking_p95_rad | tracking_max_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.1490 | 0.0563 | 0.2522 |
| `left_knee` | 0.0772 | 0.0547 | 0.5121 |
| `left_ankle` | 0.3002 | 0.0394 | 0.2213 |
| `right_hip_pitch` | 0.0853 | 0.0147 | 0.0644 |
| `right_knee` | 0.0993 | 0.0342 | 0.0531 |
| `right_ankle` | 0.1247 | 0.0742 | 0.3048 |

## Soft Prior Alignment

- not provided

## Contact States

| contact_state | count |
|---|---:|
| `(0, 1)` | 2 |
| `(1, 1)` | 98 |
