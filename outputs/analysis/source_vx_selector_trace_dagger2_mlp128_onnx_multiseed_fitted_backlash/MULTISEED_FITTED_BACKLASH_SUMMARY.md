# DAgger-2 MLP ONNX Multi-Seed Fitted-Bridge Backlash Summary
status: `HOLD_DAGGER2_ONNX_BACKLASH_LOW_FORWARD_PROGRESS`
This is an offline CPU/JAX/MJX evaluation artifact on `flat_terrain_backlash`. No robot test, SSH, deploy, training, or runtime behavior change was performed.
## Aggregate
- duration_complete_count: `8 / 8`
- moving_seed_count_ratio_ge_0p5: `7 / 8`
- moving_seed_count_vx_ge_0p02: `8 / 8`
- mean_local_vx_m_s: min `0.0393`, mean `0.0433`, max `0.0459`
- track_ratio: min `0.4914`, mean `0.5409`, max `0.5741`
- pitch_chain_sent_target_velocity_p95_max_rad_s: min `4.5943`, mean `4.7138`, max `4.8522`
- pitch_chain_joint_tracking_p95_max_rad: min `0.2626`, mean `0.2637`, max `0.2650`
- base_height_min_m: min `0.1462`, mean `0.1529`, max `0.1560`
- body_pitch_abs_p95_rad: min `0.0986`, mean `0.1013`, max `0.1047`

## Per Seed
| seed | status | samples | term | mean_vx | ratio | sent_vel_p95_max | tracking_p95_max | height_min | pitch_p95 | worst_pitch_joint |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0455 | 0.5686 | 4.6275 | 0.2638 | 0.1520 | 0.0986 | `right_knee` |
| 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0418 | 0.5221 | 4.8195 | 0.2650 | 0.1556 | 0.1014 | `right_knee` |
| 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0459 | 0.5741 | 4.8522 | 0.2626 | 0.1509 | 0.1012 | `right_knee` |
| 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0393 | 0.4914 | 4.6782 | 0.2628 | 0.1560 | 0.1009 | `right_knee` |
| 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0439 | 0.5488 | 4.5943 | 0.2634 | 0.1506 | 0.1012 | `right_knee` |
| 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0456 | 0.5699 | 4.6522 | 0.2649 | 0.1462 | 0.1047 | `right_knee` |
| 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0410 | 0.5128 | 4.7304 | 0.2631 | 0.1557 | 0.1024 | `right_knee` |
| 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0431 | 0.5391 | 4.7560 | 0.2641 | 0.1559 | 0.1000 | `right_knee` |

## Interpretation
- The task-matched backlash eval still holds; inspect per-seed rows before promotion.
- This run shows the earlier flat-terrain multi-seed hold was at least partly a task mismatch relative to the DAgger smoke gate.
- This is still offline-only. Stress-bridge and robot validation remain blocked.
