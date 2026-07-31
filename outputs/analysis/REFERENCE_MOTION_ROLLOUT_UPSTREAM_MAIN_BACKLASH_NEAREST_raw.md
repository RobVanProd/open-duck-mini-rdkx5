# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
playground_path: `/tmp/open_duck_playground_origin_main`
task: `flat_terrain_backlash`
command_x: `0.074`
command_y: `-0.037`
command_yaw: `-0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `raw`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `1`
- duration_complete: `7`
- track_ratio_mean: `-0.6763`
- vx_mean: `-0.0500`
- samples_mean: `225.5000`
- vy_abs_p95_mean: `0.2314`
- action_saturation_pct_mean: `8.1751`
- reference_target_clip_p95_mean: `0.0753`
- joint_tracking_p95_mean: `0.1845`
- reference_contact_mismatch_pct_mean: `66.9833`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | -0.0114 | -0.1538 | 0.2043 | 0.1518 | 8.1714 | 0.0760 | 5.2400 | 0.1852 | 63.6000 |
| 1 | 250 | `duration_complete` | -0.0095 | -0.1287 | 0.2463 | 0.1556 | 8.1714 | 0.0760 | 5.2400 | 0.1815 | 66.0000 |
| 2 | 250 | `duration_complete` | -0.0110 | -0.1481 | 0.2136 | 0.1512 | 8.1714 | 0.0760 | 5.2400 | 0.1816 | 64.0000 |
| 3 | 250 | `duration_complete` | -0.0267 | -0.3614 | 0.2277 | 0.1542 | 8.1714 | 0.0760 | 5.2400 | 0.1849 | 67.2000 |
| 4 | 54 | `fall_or_nan` | -0.2804 | -3.7896 | 0.2921 | 0.0869 | 8.2011 | 0.0706 | 5.2334 | 0.2015 | 66.6667 |
| 5 | 250 | `duration_complete` | -0.0159 | -0.2144 | 0.2237 | 0.1467 | 8.1714 | 0.0760 | 5.2400 | 0.1821 | 71.2000 |
| 6 | 250 | `duration_complete` | -0.0218 | -0.2949 | 0.2247 | 0.1552 | 8.1714 | 0.0760 | 5.2400 | 0.1784 | 65.2000 |
| 7 | 250 | `duration_complete` | -0.0236 | -0.3193 | 0.2190 | 0.1528 | 8.1714 | 0.0760 | 5.2400 | 0.1811 | 72.0000 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0114 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.0816 |
| left_hip_pitch | 21.6186 | 0.1471 | 5.2400 | 0.1744 |
| left_knee | 21.6186 | 0.1639 | 5.2400 | 0.2634 |
| left_ankle | 18.4035 | 0.1097 | 4.9191 | 0.2026 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0107 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0074 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0033 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0026 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0149 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0678 |
| right_hip_pitch | 22.7827 | 0.1900 | 4.6448 | 0.1701 |
| right_knee | 15.5765 | 0.3088 | 5.2400 | 0.2477 |
| right_ankle | 14.4124 | 0.0490 | 5.2400 | 0.2054 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
