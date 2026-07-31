# DAgger-2 Rate-Regularized MLP ONNX Screen
status: `HOLD_RATE_REG_ONNX_SCREEN_TARGET_RATE`
Offline task-matched standard ONNX screen on `flat_terrain_backlash`, fitted bridge, seeds `0` and `3`, 10s. No robot test, SSH, deploy, training beyond this offline fit, or runtime behavior change was performed.

## Aggregate
- duration_complete_count: `2 / 2`
- moving_seed_count_ratio_ge_0p5: `0 / 2`
- mean_track_ratio: `0.4104`
- mean_local_vx_m_s: `0.0328`
- max_pitch_chain_sent_target_velocity_p95_rad_s: `3.6419`
- max_pitch_chain_joint_tracking_p95_rad: `0.2461`

## Per Seed
| seed | status | samples | term | mean_vx | ratio | sent_vel_p95_max | tracking_p95_max | height_min |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0367 | 0.4592 | 3.6419 | 0.2461 | 0.1520 |
| 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0289 | 0.3616 | 3.6396 | 0.2458 | 0.1552 |

## Interpretation
- The rate-regularized MLP still exceeds the fitted pitch-chain target-rate envelope in the standard ONNX path.
- It is not worth a full eight-seed standard ONNX gate in this form.
