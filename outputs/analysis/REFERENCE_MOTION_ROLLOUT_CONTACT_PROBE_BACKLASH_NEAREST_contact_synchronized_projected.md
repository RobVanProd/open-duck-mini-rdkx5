# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
playground_path: `/tmp/open_duck_playground_origin_main_contact_probe`
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
- track_ratio_mean: `-0.5066`
- vx_mean: `-0.0375`
- samples_mean: `224.6250`
- vy_abs_p95_mean: `0.1303`
- action_saturation_pct_mean: `0.8055`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1138`
- reference_contact_mismatch_pct_mean: `4.6415`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | 0.0046 | 0.0627 | 0.0987 | 0.1522 | 0.7143 | 0.0000 | 5.1515 | 0.1081 | 0.4000 |
| 1 | 250 | `duration_complete` | -0.0022 | -0.0302 | 0.1118 | 0.1551 | 0.7429 | 0.0000 | 5.1069 | 0.1106 | 1.6000 |
| 2 | 250 | `duration_complete` | 0.0047 | 0.0637 | 0.0994 | 0.1510 | 0.7429 | 0.0000 | 5.1515 | 0.1084 | 1.2000 |
| 3 | 250 | `duration_complete` | -0.0080 | -0.1077 | 0.0998 | 0.1503 | 0.7429 | 0.0000 | 5.1515 | 0.1102 | 0.8000 |
| 4 | 47 | `fall_or_nan` | -0.3206 | -4.3326 | 0.2630 | 0.0716 | 1.2158 | 0.0000 | 5.2400 | 0.1533 | 25.5319 |
| 5 | 250 | `duration_complete` | 0.0132 | 0.1782 | 0.1250 | 0.1467 | 0.7429 | 0.0000 | 5.1515 | 0.1060 | 3.6000 |
| 6 | 250 | `duration_complete` | 0.0055 | 0.0740 | 0.1409 | 0.1554 | 0.7714 | 0.0000 | 4.2321 | 0.1080 | 1.6000 |
| 7 | 250 | `duration_complete` | 0.0029 | 0.0393 | 0.1038 | 0.1541 | 0.7714 | 0.0000 | 4.5898 | 0.1061 | 2.4000 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.2442 | 0.0098 |
| left_hip_roll | 0.0000 | 0.0000 | 5.2400 | 0.1147 |
| left_hip_pitch | 0.3339 | 0.0000 | 5.2400 | 0.0786 |
| left_knee | 0.2226 | 0.0000 | 5.1515 | 0.1165 |
| left_ankle | 9.6272 | 0.0000 | 5.2400 | 0.1249 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0107 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0060 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0013 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0009 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.4306 | 0.0098 |
| right_hip_roll | 0.0000 | 0.0000 | 2.9256 | 0.0913 |
| right_hip_pitch | 0.4452 | 0.0000 | 5.2400 | 0.0796 |
| right_knee | 0.0000 | 0.0000 | 1.2437 | 0.0707 |
| right_ankle | 0.0000 | 0.0000 | 5.2400 | 0.0863 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
