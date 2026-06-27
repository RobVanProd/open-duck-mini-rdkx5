# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_LOW_PROGRESS`
playground_path: `/tmp/open_duck_playground_origin_main`
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
- track_ratio_mean: `-0.1544`
- vx_mean: `-0.0114`
- samples_mean: `250.0000`
- vy_abs_p95_mean: `0.1691`
- action_saturation_pct_mean: `1.0571`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1343`
- reference_contact_mismatch_pct_mean: `72.9500`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | -0.0143 | -0.1931 | 0.1766 | 0.1518 | 1.0571 | 0.0000 | 3.3791 | 0.1329 | 74.0000 |
| 1 | 250 | `duration_complete` | -0.0088 | -0.1190 | 0.1806 | 0.1555 | 1.0571 | 0.0000 | 3.3791 | 0.1353 | 71.6000 |
| 2 | 250 | `duration_complete` | -0.0054 | -0.0736 | 0.1691 | 0.1512 | 1.0571 | 0.0000 | 3.3791 | 0.1342 | 76.0000 |
| 3 | 250 | `duration_complete` | -0.0212 | -0.2864 | 0.1686 | 0.1541 | 1.0571 | 0.0000 | 3.3791 | 0.1338 | 73.2000 |
| 4 | 250 | `duration_complete` | -0.0091 | -0.1232 | 0.1556 | 0.1506 | 1.0571 | 0.0000 | 3.3791 | 0.1340 | 72.4000 |
| 5 | 250 | `duration_complete` | -0.0055 | -0.0740 | 0.1778 | 0.1467 | 1.0571 | 0.0000 | 3.3791 | 0.1353 | 72.8000 |
| 6 | 250 | `duration_complete` | -0.0159 | -0.2155 | 0.1726 | 0.1560 | 1.0571 | 0.0000 | 3.3791 | 0.1350 | 72.0000 |
| 7 | 250 | `duration_complete` | -0.0111 | -0.1500 | 0.1520 | 0.1559 | 1.0571 | 0.0000 | 3.3791 | 0.1343 | 71.6000 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0114 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.0839 |
| left_hip_pitch | 3.6000 | 0.0000 | 3.1839 | 0.1380 |
| left_knee | 3.6000 | 0.0000 | 5.1326 | 0.2311 |
| left_ankle | 3.6000 | 0.0000 | 3.4038 | 0.1456 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0109 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0076 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0026 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0022 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0127 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0612 |
| right_hip_pitch | 4.0000 | 0.0000 | 3.3791 | 0.1260 |
| right_knee | 0.0000 | 0.0000 | 4.2533 | 0.1887 |
| right_ankle | 0.0000 | 0.0000 | 3.1548 | 0.1366 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
