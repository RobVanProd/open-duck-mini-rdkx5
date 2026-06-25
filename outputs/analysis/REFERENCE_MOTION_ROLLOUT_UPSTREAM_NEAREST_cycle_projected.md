# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `cycle_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `8`
- duration_complete: `0`
- track_ratio_mean: `-0.1163`
- vx_mean: `-0.0086`
- samples_mean: `66.8750`
- vy_abs_p95_mean: `0.4028`
- action_saturation_pct_mean: `1.1550`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1514`
- reference_contact_mismatch_pct_mean: `71.1627`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 70 | `fall_or_nan` | 0.0013 | 0.0177 | 0.1447 | 0.1534 | 1.2245 | 0.0000 | 3.2680 | 0.1483 | 72.8571 |
| 1 | 34 | `fall_or_nan` | -0.0781 | -1.0553 | 1.1292 | 0.0934 | 1.0504 | 0.0000 | 3.3736 | 0.1553 | 61.7647 |
| 2 | 70 | `fall_or_nan` | 0.0106 | 0.1435 | 0.1760 | 0.1526 | 1.2245 | 0.0000 | 3.2680 | 0.1504 | 67.1429 |
| 3 | 70 | `fall_or_nan` | -0.0195 | -0.2634 | 0.1741 | 0.1540 | 1.2245 | 0.0000 | 3.2680 | 0.1444 | 77.1429 |
| 4 | 70 | `fall_or_nan` | 0.0125 | 0.1689 | 0.1758 | 0.1518 | 1.2245 | 0.0000 | 3.2680 | 0.1464 | 71.4286 |
| 5 | 116 | `fall_or_nan` | 0.0142 | 0.1921 | 0.1950 | 0.1471 | 1.0468 | 0.0000 | 3.3291 | 0.1544 | 68.9655 |
| 6 | 70 | `fall_or_nan` | -0.0200 | -0.2696 | 0.2536 | 0.1567 | 1.2245 | 0.0000 | 3.2680 | 0.1533 | 72.8571 |
| 7 | 35 | `fall_or_nan` | 0.0101 | 0.1361 | 0.9737 | 0.1080 | 1.0204 | 0.0000 | 3.2958 | 0.1584 | 77.1429 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0144 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.1072 |
| left_hip_pitch | 3.9252 | 0.0000 | 3.1839 | 0.1498 |
| left_knee | 3.9252 | 0.0000 | 5.1326 | 0.2552 |
| left_ankle | 3.9252 | 0.0000 | 3.4038 | 0.1671 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0124 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0086 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0034 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0010 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0159 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0844 |
| right_hip_pitch | 4.4860 | 0.0000 | 3.5156 | 0.1310 |
| right_knee | 0.0000 | 0.0000 | 4.2533 | 0.2044 |
| right_ankle | 0.0000 | 0.0000 | 3.1548 | 0.1668 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
