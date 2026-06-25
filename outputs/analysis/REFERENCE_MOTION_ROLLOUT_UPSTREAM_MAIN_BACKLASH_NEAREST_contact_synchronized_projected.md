# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
playground_path: `/tmp/open_duck_playground_origin_main`
task: `flat_terrain_backlash`
command_x: `0.074`
command_y: `-0.037`
command_yaw: `-0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `contact_synchronized_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `1`
- duration_complete: `7`
- track_ratio_mean: `0.4073`
- vx_mean: `0.0301`
- samples_mean: `229.0000`
- vy_abs_p95_mean: `0.1347`
- action_saturation_pct_mean: `0.7985`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1078`
- reference_contact_mismatch_pct_mean: `20.1366`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | 0.0036 | 0.0482 | 0.1188 | 0.1521 | 0.8286 | 0.0000 | 5.2400 | 0.1071 | 19.2000 |
| 1 | 250 | `duration_complete` | 0.0001 | 0.0019 | 0.1419 | 0.1559 | 0.8000 | 0.0000 | 5.2400 | 0.1010 | 20.0000 |
| 2 | 250 | `duration_complete` | 0.0063 | 0.0846 | 0.1089 | 0.1512 | 0.7143 | 0.0000 | 5.2400 | 0.0957 | 18.8000 |
| 3 | 250 | `duration_complete` | -0.0083 | -0.1120 | 0.1214 | 0.1507 | 0.6571 | 0.0000 | 5.2400 | 0.1080 | 22.0000 |
| 4 | 82 | `fall_or_nan` | 0.2310 | 3.1223 | 0.1625 | 0.0070 | 1.0453 | 0.0000 | 5.2400 | 0.1368 | 18.2927 |
| 5 | 250 | `duration_complete` | 0.0095 | 0.1283 | 0.1531 | 0.1467 | 0.8571 | 0.0000 | 5.2400 | 0.1074 | 18.4000 |
| 6 | 250 | `duration_complete` | -0.0011 | -0.0143 | 0.1435 | 0.1528 | 0.8000 | 0.0000 | 5.2400 | 0.1058 | 21.2000 |
| 7 | 250 | `duration_complete` | -0.0000 | -0.0004 | 0.1270 | 0.1558 | 0.6857 | 0.0000 | 5.2400 | 0.1008 | 23.2000 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.2442 | 0.0102 |
| left_hip_roll | 0.0000 | 0.0000 | 5.2400 | 0.1149 |
| left_hip_pitch | 0.7096 | 0.0000 | 5.2400 | 0.1317 |
| left_knee | 0.5459 | 0.0000 | 5.2400 | 0.1361 |
| left_ankle | 9.1157 | 0.0000 | 5.2400 | 0.1372 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0123 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0070 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0026 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0014 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.6345 | 0.0129 |
| right_hip_roll | 0.0000 | 0.0000 | 2.9256 | 0.0845 |
| right_hip_pitch | 0.4913 | 0.0000 | 5.2400 | 0.1053 |
| right_knee | 0.0000 | 0.0000 | 3.4371 | 0.0911 |
| right_ankle | 0.0000 | 0.0000 | 5.2400 | 0.0922 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
