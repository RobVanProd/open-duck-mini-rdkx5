# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `contact_synchronized_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `2`
- duration_complete: `6`
- track_ratio_mean: `-0.1715`
- vx_mean: `-0.0127`
- samples_mean: `196.7500`
- vy_abs_p95_mean: `0.3713`
- action_saturation_pct_mean: `1.0597`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1117`
- reference_contact_mismatch_pct_mean: `14.6741`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | 0.0041 | 0.0558 | 0.1067 | 0.1558 | 0.9714 | 0.0000 | 5.2400 | 0.1030 | 20.4000 |
| 1 | 32 | `fall_or_nan` | -0.1372 | -1.8546 | 1.0684 | 0.1040 | 0.8929 | 0.0000 | 4.0303 | 0.1533 | 6.2500 |
| 2 | 250 | `duration_complete` | 0.0061 | 0.0827 | 0.1066 | 0.1527 | 0.9429 | 0.0000 | 5.2400 | 0.0980 | 16.8000 |
| 3 | 250 | `duration_complete` | -0.0013 | -0.0172 | 0.1204 | 0.1598 | 0.9429 | 0.0000 | 5.1515 | 0.0969 | 13.6000 |
| 4 | 250 | `duration_complete` | 0.0105 | 0.1414 | 0.1084 | 0.1518 | 1.0000 | 0.0000 | 5.2400 | 0.0923 | 18.0000 |
| 5 | 250 | `duration_complete` | 0.0132 | 0.1789 | 0.1143 | 0.1471 | 0.9714 | 0.0000 | 5.2400 | 0.1039 | 19.2000 |
| 6 | 250 | `duration_complete` | 0.0028 | 0.0383 | 0.1261 | 0.1586 | 0.8857 | 0.0000 | 5.2400 | 0.1017 | 16.0000 |
| 7 | 42 | `fall_or_nan` | 0.0002 | 0.0025 | 1.2195 | 0.0525 | 1.8707 | 0.0000 | 4.5773 | 0.1446 | 7.1429 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.2442 | 0.0113 |
| left_hip_roll | 0.0000 | 0.0000 | 5.2400 | 0.1100 |
| left_hip_pitch | 0.6989 | 0.0000 | 5.2400 | 0.0970 |
| left_knee | 0.6989 | 0.0000 | 5.2400 | 0.1359 |
| left_ankle | 11.6900 | 0.0000 | 5.2400 | 0.1244 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0123 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0067 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0014 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0013 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.6345 | 0.0122 |
| right_hip_roll | 0.0000 | 0.0000 | 2.9256 | 0.0858 |
| right_hip_pitch | 0.5718 | 0.0000 | 5.2400 | 0.0981 |
| right_knee | 0.0000 | 0.0000 | 3.0102 | 0.0888 |
| right_ankle | 0.0000 | 0.0000 | 5.2400 | 0.0815 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
