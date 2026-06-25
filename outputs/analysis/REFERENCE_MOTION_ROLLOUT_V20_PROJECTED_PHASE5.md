# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.04`
duration_s: `5.0`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`
reference_target_mode: `cycle_projected`
first_reference_phase: `5`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- track_ratio_mean: `-0.4917`
- vx_mean: `-0.0197`
- samples_mean: `81.6250`
- vy_abs_p95_mean: `0.4124`
- action_saturation_pct_mean: `1.0697`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1479`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | `fall_or_nan` | 0.0040 | 0.0995 | 0.1457 | 0.1537 | 1.1224 | 0.0000 | 3.1544 | 0.1485 |
| 1 | 33 | `fall_or_nan` | -0.1382 | -3.4539 | 1.0397 | 0.1036 | 1.0823 | 0.0000 | 3.0508 | 0.1475 |
| 2 | 83 | `fall_or_nan` | 0.0077 | 0.1937 | 0.1616 | 0.1526 | 1.0327 | 0.0000 | 3.1536 | 0.1540 |
| 3 | 70 | `fall_or_nan` | -0.0167 | -0.4178 | 0.1408 | 0.1559 | 1.1224 | 0.0000 | 3.1544 | 0.1399 |
| 4 | 110 | `fall_or_nan` | 0.0077 | 0.1923 | 0.1543 | 0.1517 | 1.0390 | 0.0000 | 3.1536 | 0.1448 |
| 5 | 180 | `fall_or_nan` | 0.0078 | 0.1949 | 0.1617 | 0.1471 | 1.0714 | 0.0000 | 3.1536 | 0.1434 |
| 6 | 70 | `fall_or_nan` | -0.0074 | -0.1853 | 0.2633 | 0.1569 | 1.1224 | 0.0000 | 3.1544 | 0.1608 |
| 7 | 37 | `fall_or_nan` | -0.0223 | -0.5568 | 1.2325 | 0.0805 | 0.9653 | 0.0000 | 3.1457 | 0.1445 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1429 | 0.0127 |
| left_hip_roll | 0.0000 | 0.0000 | 1.3391 | 0.0827 |
| left_hip_pitch | 3.8285 | 0.0000 | 3.0986 | 0.1357 |
| left_knee | 3.8285 | 0.0000 | 4.7357 | 0.2666 |
| left_ankle | 4.1348 | 0.0000 | 3.3211 | 0.1689 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0127 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0078 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0026 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0012 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1353 | 0.0151 |
| right_hip_roll | 0.0000 | 0.0000 | 1.3495 | 0.0800 |
| right_hip_pitch | 3.2159 | 0.0000 | 2.9364 | 0.1163 |
| right_knee | 0.0000 | 0.0000 | 3.9759 | 0.1986 |
| right_ankle | 0.0000 | 0.0000 | 3.5144 | 0.1820 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
