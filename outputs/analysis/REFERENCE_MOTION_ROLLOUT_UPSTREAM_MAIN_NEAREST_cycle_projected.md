# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `cycle_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `2`
- duration_complete: `6`
- track_ratio_mean: `-0.1624`
- vx_mean: `-0.0120`
- samples_mean: `196.1250`
- vy_abs_p95_mean: `0.3897`
- action_saturation_pct_mean: `1.0517`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1476`
- reference_contact_mismatch_pct_mean: `71.4134`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | -0.0077 | -0.1039 | 0.1700 | 0.1534 | 1.0571 | 0.0000 | 3.3791 | 0.1433 | 75.2000 |
| 1 | 34 | `fall_or_nan` | -0.0781 | -1.0553 | 1.1292 | 0.0934 | 1.0504 | 0.0000 | 3.3736 | 0.1553 | 61.7647 |
| 2 | 250 | `duration_complete` | -0.0008 | -0.0114 | 0.1694 | 0.1526 | 1.0571 | 0.0000 | 3.3791 | 0.1445 | 70.0000 |
| 3 | 250 | `duration_complete` | -0.0102 | -0.1381 | 0.1698 | 0.1540 | 1.0571 | 0.0000 | 3.3791 | 0.1431 | 72.0000 |
| 4 | 250 | `duration_complete` | -0.0019 | -0.0251 | 0.1579 | 0.1518 | 1.0571 | 0.0000 | 3.3791 | 0.1441 | 70.8000 |
| 5 | 250 | `duration_complete` | 0.0046 | 0.0619 | 0.1801 | 0.1471 | 1.0571 | 0.0000 | 3.3791 | 0.1467 | 72.0000 |
| 6 | 250 | `duration_complete` | -0.0121 | -0.1635 | 0.1679 | 0.1567 | 1.0571 | 0.0000 | 3.3791 | 0.1456 | 72.4000 |
| 7 | 35 | `fall_or_nan` | 0.0101 | 0.1361 | 0.9737 | 0.1080 | 1.0204 | 0.0000 | 3.2958 | 0.1584 | 77.1429 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0140 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.1049 |
| left_hip_pitch | 3.5692 | 0.0000 | 3.1839 | 0.1415 |
| left_knee | 3.5692 | 0.0000 | 5.1326 | 0.2544 |
| left_ankle | 3.5692 | 0.0000 | 3.4038 | 0.1609 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0112 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0092 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0032 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0012 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0158 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0763 |
| right_hip_pitch | 4.0790 | 0.0000 | 3.3791 | 0.1213 |
| right_knee | 0.0000 | 0.0000 | 4.2533 | 0.2045 |
| right_ankle | 0.0000 | 0.0000 | 3.1548 | 0.1633 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
