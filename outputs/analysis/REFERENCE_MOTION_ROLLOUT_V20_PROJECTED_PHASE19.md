# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.04`
duration_s: `5.0`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`
reference_target_mode: `cycle_projected`
first_reference_phase: `19`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- track_ratio_mean: `-1.2155`
- vx_mean: `-0.0486`
- samples_mean: `69.3750`
- vy_abs_p95_mean: `0.3951`
- action_saturation_pct_mean: `0.9422`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1510`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | `fall_or_nan` | 0.0055 | 0.1367 | 0.1489 | 0.1559 | 0.9184 | 0.0000 | 3.1536 | 0.1556 |
| 1 | 34 | `fall_or_nan` | -0.0991 | -2.4787 | 1.0329 | 0.0995 | 0.8403 | 0.0000 | 3.0896 | 0.1455 |
| 2 | 111 | `fall_or_nan` | 0.0074 | 0.1844 | 0.1539 | 0.1527 | 1.0296 | 0.0000 | 3.1537 | 0.1418 |
| 3 | 70 | `fall_or_nan` | -0.0196 | -0.4900 | 0.1550 | 0.1570 | 0.9184 | 0.0000 | 3.1536 | 0.1481 |
| 4 | 112 | `fall_or_nan` | 0.0079 | 0.1983 | 0.1570 | 0.1517 | 1.0204 | 0.0000 | 3.1536 | 0.1420 |
| 5 | 52 | `fall_or_nan` | -0.2814 | -7.0343 | 0.1650 | 0.0707 | 1.0989 | 0.0000 | 3.1193 | 0.1732 |
| 6 | 70 | `fall_or_nan` | -0.0170 | -0.4249 | 0.2902 | 0.1569 | 0.9184 | 0.0000 | 3.1536 | 0.1486 |
| 7 | 36 | `fall_or_nan` | 0.0074 | 0.1842 | 1.0580 | 0.0894 | 0.7937 | 0.0000 | 3.1298 | 0.1535 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1429 | 0.0138 |
| left_hip_roll | 0.0000 | 0.0000 | 1.3391 | 0.0868 |
| left_hip_pitch | 3.2432 | 0.0000 | 3.0986 | 0.1297 |
| left_knee | 3.2432 | 0.0000 | 4.7357 | 0.2500 |
| left_ankle | 3.2432 | 0.0000 | 3.3211 | 0.1661 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0128 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0073 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0028 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0016 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1353 | 0.0137 |
| right_hip_roll | 0.0000 | 0.0000 | 1.3495 | 0.0815 |
| right_hip_pitch | 3.7838 | 0.0000 | 2.9364 | 0.1267 |
| right_knee | 0.0000 | 0.0000 | 3.9759 | 0.2051 |
| right_ankle | 0.0000 | 0.0000 | 3.5144 | 0.1919 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
