# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_LOW_PROGRESS`
playground_path: `/tmp/open_duck_playground_origin_main_contact_probe`
task: `flat_terrain_backlash`
command_x: `0.074`
command_y: `-0.037`
command_yaw: `-0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `cycle_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `0`
- duration_complete: `8`
- track_ratio_mean: `-0.1628`
- vx_mean: `-0.0120`
- samples_mean: `250.0000`
- vy_abs_p95_mean: `0.1676`
- action_saturation_pct_mean: `1.0571`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1344`
- reference_contact_mismatch_pct_mean: `66.9500`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | -0.0106 | -0.1428 | 0.1664 | 0.1519 | 1.0571 | 0.0000 | 3.3791 | 0.1332 | 66.8000 |
| 1 | 250 | `duration_complete` | -0.0128 | -0.1728 | 0.1804 | 0.1545 | 1.0571 | 0.0000 | 3.3791 | 0.1355 | 66.8000 |
| 2 | 250 | `duration_complete` | -0.0068 | -0.0920 | 0.1578 | 0.1510 | 1.0571 | 0.0000 | 3.3791 | 0.1344 | 65.2000 |
| 3 | 250 | `duration_complete` | -0.0209 | -0.2820 | 0.1660 | 0.1525 | 1.0571 | 0.0000 | 3.3791 | 0.1337 | 66.4000 |
| 4 | 250 | `duration_complete` | -0.0120 | -0.1624 | 0.1565 | 0.1507 | 1.0571 | 0.0000 | 3.3791 | 0.1333 | 68.0000 |
| 5 | 250 | `duration_complete` | -0.0038 | -0.0513 | 0.1817 | 0.1467 | 1.0571 | 0.0000 | 3.3791 | 0.1366 | 68.4000 |
| 6 | 250 | `duration_complete` | -0.0160 | -0.2167 | 0.1764 | 0.1550 | 1.0571 | 0.0000 | 3.3791 | 0.1345 | 67.6000 |
| 7 | 250 | `duration_complete` | -0.0135 | -0.1827 | 0.1556 | 0.1541 | 1.0571 | 0.0000 | 3.3791 | 0.1341 | 66.4000 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0129 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.0889 |
| left_hip_pitch | 3.6000 | 0.0000 | 3.1839 | 0.1371 |
| left_knee | 3.6000 | 0.0000 | 5.1326 | 0.2322 |
| left_ankle | 3.6000 | 0.0000 | 3.4038 | 0.1466 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0086 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0056 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0022 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0011 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0123 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0606 |
| right_hip_pitch | 4.0000 | 0.0000 | 3.3791 | 0.1333 |
| right_knee | 0.0000 | 0.0000 | 4.2533 | 0.1910 |
| right_ankle | 0.0000 | 0.0000 | 3.1548 | 0.1352 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
