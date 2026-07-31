# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `contact_synchronized_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- track_ratio_mean: `-0.1453`
- vx_mean: `-0.0108`
- samples_mean: `89.0000`
- vy_abs_p95_mean: `0.3959`
- action_saturation_pct_mean: `1.0862`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1226`
- reference_contact_mismatch_pct_mean: `14.5439`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | `fall_or_nan` | 0.0120 | 0.1622 | 0.1201 | 0.1558 | 1.1224 | 0.0000 | 5.2400 | 0.1273 | 20.0000 |
| 1 | 32 | `fall_or_nan` | -0.1372 | -1.8546 | 1.0684 | 0.1040 | 0.8929 | 0.0000 | 4.0303 | 0.1533 | 6.2500 |
| 2 | 75 | `fall_or_nan` | 0.0146 | 0.1971 | 0.1105 | 0.1527 | 0.9524 | 0.0000 | 5.2400 | 0.1097 | 21.3333 |
| 3 | 70 | `fall_or_nan` | -0.0103 | -0.1388 | 0.1598 | 0.1598 | 1.0204 | 0.0000 | 5.2179 | 0.1182 | 17.1429 |
| 4 | 151 | `fall_or_nan` | 0.0147 | 0.1992 | 0.1068 | 0.1518 | 0.9934 | 0.0000 | 5.2400 | 0.0963 | 15.2318 |
| 5 | 202 | `fall_or_nan` | 0.0148 | 0.1993 | 0.1241 | 0.1471 | 0.9194 | 0.0000 | 5.2400 | 0.1093 | 17.8218 |
| 6 | 70 | `fall_or_nan` | 0.0052 | 0.0707 | 0.2581 | 0.1586 | 0.9184 | 0.0000 | 5.2400 | 0.1219 | 11.4286 |
| 7 | 42 | `fall_or_nan` | 0.0002 | 0.0025 | 1.2195 | 0.0525 | 1.8707 | 0.0000 | 4.5773 | 0.1446 | 7.1429 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.2442 | 0.0129 |
| left_hip_roll | 0.0000 | 0.0000 | 5.2400 | 0.1188 |
| left_hip_pitch | 1.5449 | 0.0000 | 5.2400 | 0.1250 |
| left_knee | 1.5449 | 0.0000 | 5.2400 | 0.1892 |
| left_ankle | 9.9719 | 0.0000 | 5.2400 | 0.1405 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0138 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0069 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0019 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0014 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.5513 | 0.0125 |
| right_hip_roll | 0.0000 | 0.0000 | 2.9256 | 0.0915 |
| right_hip_pitch | 1.2640 | 0.0000 | 5.2400 | 0.1224 |
| right_knee | 0.0000 | 0.0000 | 3.7420 | 0.1277 |
| right_ankle | 0.0000 | 0.0000 | 5.2400 | 0.1271 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
