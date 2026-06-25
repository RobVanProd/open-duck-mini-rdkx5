# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.04`
duration_s: `5.0`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`
reference_target_mode: `cycle_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- track_ratio_mean: `-0.2495`
- vx_mean: `-0.0100`
- samples_mean: `83.0000`
- vy_abs_p95_mean: `0.4017`
- action_saturation_pct_mean: `1.1454`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1440`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | `fall_or_nan` | 0.0017 | 0.0425 | 0.1458 | 0.1534 | 1.2245 | 0.0000 | 3.1536 | 0.1420 |
| 1 | 34 | `fall_or_nan` | -0.0835 | -2.0880 | 1.1441 | 0.0932 | 1.0504 | 0.0000 | 3.1536 | 0.1467 |
| 2 | 88 | `fall_or_nan` | 0.0080 | 0.1992 | 0.1500 | 0.1526 | 1.0552 | 0.0000 | 3.1538 | 0.1405 |
| 3 | 70 | `fall_or_nan` | -0.0108 | -0.2690 | 0.1564 | 0.1552 | 1.2245 | 0.0000 | 3.1536 | 0.1347 |
| 4 | 101 | `fall_or_nan` | 0.0079 | 0.1981 | 0.1489 | 0.1518 | 1.1315 | 0.0000 | 3.1546 | 0.1412 |
| 5 | 195 | `fall_or_nan` | 0.0078 | 0.1961 | 0.1618 | 0.1471 | 1.0623 | 0.0000 | 3.1546 | 0.1422 |
| 6 | 70 | `fall_or_nan` | -0.0119 | -0.2982 | 0.2534 | 0.1565 | 1.2245 | 0.0000 | 3.1536 | 0.1480 |
| 7 | 36 | `fall_or_nan` | 0.0009 | 0.0230 | 1.0530 | 0.0947 | 1.1905 | 0.0000 | 3.1298 | 0.1564 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1429 | 0.0131 |
| left_hip_roll | 0.0000 | 0.0000 | 1.3391 | 0.0871 |
| left_hip_pitch | 3.7651 | 0.0000 | 3.0986 | 0.1303 |
| left_knee | 3.7651 | 0.0000 | 4.7357 | 0.2498 |
| left_ankle | 3.9157 | 0.0000 | 3.3211 | 0.1663 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0129 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0084 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0026 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0014 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1353 | 0.0142 |
| right_hip_roll | 0.0000 | 0.0000 | 1.3495 | 0.0801 |
| right_hip_pitch | 4.3675 | 0.0000 | 3.1536 | 0.1207 |
| right_knee | 0.0000 | 0.0000 | 3.9759 | 0.1918 |
| right_ankle | 0.0000 | 0.0000 | 3.5144 | 0.1623 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
