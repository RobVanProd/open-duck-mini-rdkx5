# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.04`
duration_s: `5.0`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- track_ratio_mean: `-0.2614`
- vx_mean: `-0.0105`
- samples_mean: `79.3750`
- vy_abs_p95_mean: `0.3918`
- action_saturation_pct_mean: `6.4967`
- reference_target_clip_p95_mean: `0.0314`
- joint_tracking_p95_mean: `0.1876`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | `fall_or_nan` | -0.0028 | -0.0695 | 0.1116 | 0.1534 | 6.6327 | 0.0338 | 4.7461 | 0.1824 |
| 1 | 34 | `fall_or_nan` | -0.0886 | -2.2161 | 1.1221 | 0.0969 | 6.3025 | 0.0301 | 5.0956 | 0.2085 |
| 2 | 73 | `fall_or_nan` | 0.0079 | 0.1975 | 0.1490 | 0.1526 | 6.5558 | 0.0335 | 4.8383 | 0.1765 |
| 3 | 70 | `fall_or_nan` | -0.0208 | -0.5207 | 0.1580 | 0.1570 | 6.6327 | 0.0338 | 4.7461 | 0.1824 |
| 4 | 101 | `fall_or_nan` | 0.0079 | 0.1987 | 0.1487 | 0.1518 | 6.4356 | 0.0289 | 4.8880 | 0.1821 |
| 5 | 181 | `fall_or_nan` | 0.0078 | 0.1955 | 0.1478 | 0.1471 | 6.4325 | 0.0289 | 4.8880 | 0.1827 |
| 6 | 70 | `fall_or_nan` | -0.0050 | -0.1238 | 0.2491 | 0.1582 | 6.6327 | 0.0338 | 4.7461 | 0.1961 |
| 7 | 36 | `fall_or_nan` | 0.0099 | 0.2475 | 1.0478 | 0.1021 | 6.3492 | 0.0289 | 4.8242 | 0.1905 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1429 | 0.0154 |
| left_hip_roll | 0.0000 | 0.0000 | 1.3391 | 0.0875 |
| left_hip_pitch | 23.1496 | 0.1366 | 3.9927 | 0.1695 |
| left_knee | 15.2756 | 0.1540 | 5.2400 | 0.2909 |
| left_ankle | 12.1260 | 0.0338 | 3.9546 | 0.1978 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0107 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0088 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0029 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0011 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1353 | 0.0168 |
| right_hip_roll | 0.0000 | 0.0000 | 1.3495 | 0.0824 |
| right_hip_pitch | 18.7402 | 0.1914 | 5.1082 | 0.1414 |
| right_knee | 15.7480 | 0.3093 | 5.2400 | 0.2411 |
| right_ankle | 5.9843 | 0.0133 | 5.1066 | 0.2460 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
