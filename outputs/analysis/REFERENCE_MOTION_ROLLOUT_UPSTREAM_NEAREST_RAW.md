# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `raw`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- track_ratio_mean: `-1.1762`
- vx_mean: `-0.0870`
- samples_mean: `57.2500`
- vy_abs_p95_mean: `0.4364`
- action_saturation_pct_mean: `8.3396`
- reference_target_clip_p95_mean: `0.0751`
- joint_tracking_p95_mean: `0.2005`
- reference_contact_mismatch_pct_mean: `69.5729`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | `fall_or_nan` | -0.0037 | -0.0494 | 0.1774 | 0.1534 | 8.4694 | 0.0780 | 5.2068 | 0.1939 | 64.2857 |
| 1 | 34 | `fall_or_nan` | -0.0925 | -1.2497 | 1.1201 | 0.0949 | 7.9832 | 0.0706 | 5.2400 | 0.2092 | 76.4706 |
| 2 | 70 | `fall_or_nan` | 0.0039 | 0.0528 | 0.2112 | 0.1526 | 8.4694 | 0.0780 | 5.2068 | 0.1875 | 68.5714 |
| 3 | 70 | `fall_or_nan` | -0.0337 | -0.4550 | 0.1969 | 0.1564 | 8.4694 | 0.0780 | 5.2068 | 0.1952 | 70.0000 |
| 4 | 52 | `fall_or_nan` | -0.3034 | -4.1001 | 0.2157 | 0.0648 | 8.1044 | 0.0656 | 5.1072 | 0.1981 | 57.6923 |
| 5 | 56 | `fall_or_nan` | -0.2459 | -3.3230 | 0.3056 | 0.0820 | 8.4184 | 0.0777 | 5.2400 | 0.2139 | 66.0714 |
| 6 | 70 | `fall_or_nan` | -0.0326 | -0.4408 | 0.2491 | 0.1570 | 8.4694 | 0.0780 | 5.2068 | 0.2024 | 75.7143 |
| 7 | 36 | `fall_or_nan` | 0.0115 | 0.1556 | 1.0151 | 0.1031 | 8.3333 | 0.0749 | 5.2400 | 0.2037 | 77.7778 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0148 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.1087 |
| left_hip_pitch | 22.7074 | 0.1471 | 5.2400 | 0.1985 |
| left_knee | 23.1441 | 0.1639 | 5.2400 | 0.2994 |
| left_ankle | 20.5240 | 0.1097 | 4.9191 | 0.2151 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0130 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0083 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0034 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0010 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0181 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0904 |
| right_hip_pitch | 22.2707 | 0.1900 | 5.2400 | 0.1770 |
| right_knee | 16.3755 | 0.3088 | 5.2400 | 0.2668 |
| right_ankle | 12.2271 | 0.0490 | 5.2400 | 0.2143 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
