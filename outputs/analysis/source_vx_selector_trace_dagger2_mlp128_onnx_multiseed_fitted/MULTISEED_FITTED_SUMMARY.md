# DAgger-2 MLP ONNX Multi-Seed Fitted-Bridge Summary
status: `HOLD_DAGGER2_ONNX_MULTI_SEED_LOW_FORWARD_PROGRESS`
This is an offline CPU/JAX/MJX evaluation artifact. No robot test, SSH, deploy, training, or runtime behavior change was performed.
## Aggregate
- duration_complete_count: `6 / 8`
- moving_seed_count_ratio_ge_0p5: `0 / 8`
- moving_seed_count_vx_ge_0p02: `4 / 8`
- mean_local_vx_m_s: min `0.0160`, mean `0.0202`, max `0.0252`
- track_ratio: min `0.1999`, mean `0.2526`, max `0.3149`
- pitch_chain_sent_target_velocity_p95_max_rad_s: min `2.4613`, mean `3.5607`, max `3.9048`
- pitch_chain_joint_tracking_p95_max_rad: min `0.2126`, mean `0.2377`, max `0.3058`
- base_height_min_m: min `0.0686`, mean `0.1324`, max `0.1579`
- body_pitch_abs_p95_rad: min `0.0011`, mean `0.0406`, max `0.0564`

## Per Seed
| seed | status | samples | term | mean_vx | ratio | sent_vel_p95_max | tracking_p95_max | height_min | pitch_p95 | worst_pitch_joint |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0197 | 0.2457 | 3.8533 | 0.2177 | 0.1536 | 0.0478 | `right_knee` |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0160 | 0.1999 | 2.4613 | 0.3055 | 0.0686 | 0.0011 | `right_knee` |
| 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0228 | 0.2855 | 3.7855 | 0.2152 | 0.1525 | 0.0494 | `right_knee` |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0177 | 0.2207 | 3.7090 | 0.2135 | 0.1579 | 0.0564 | `right_knee` |
| 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0215 | 0.2691 | 3.8785 | 0.2158 | 0.1515 | 0.0558 | `right_knee` |
| 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0252 | 0.3149 | 3.9048 | 0.2152 | 0.1467 | 0.0490 | `right_knee` |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0164 | 0.2051 | 3.8711 | 0.2126 | 0.1576 | 0.0563 | `right_knee` |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | 0.0224 | 0.2797 | 3.0224 | 0.3058 | 0.0710 | 0.0094 | `left_ankle` |

## Interpretation
- All eight seeds were evaluated without action saturation, but only six completed the 10s fitted-bridge rollout.
- The candidate remains a hold because forward progress is weak: no seed reaches track ratio >= 0.5 and only four seeds reach mean local vx >= 0.02 m/s.
- Seeds 1 and 7 terminate early with low base height.
- This supports keeping the ONNX as an exportability milestone, not a robot candidate.
