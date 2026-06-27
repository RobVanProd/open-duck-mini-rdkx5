# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
playground_path: `/tmp/open_duck_playground_origin_main_contact_probe`
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
- falls: `3`
- duration_complete: `5`
- track_ratio_mean: `0.2816`
- vx_mean: `0.0208`
- samples_mean: `182.1250`
- vy_abs_p95_mean: `0.2152`
- action_saturation_pct_mean: `8.1515`
- reference_target_clip_p95_mean: `0.0744`
- joint_tracking_p95_mean: `0.1940`
- reference_contact_mismatch_pct_mean: `67.2202`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 78 | `fall_or_nan` | 0.2418 | 3.2680 | 0.1918 | 0.0059 | 8.0586 | 0.0688 | 5.1271 | 0.1921 | 64.1026 |
| 1 | 75 | `fall_or_nan` | 0.2544 | 3.4374 | 0.2759 | 0.0060 | 8.0952 | 0.0760 | 5.2400 | 0.1937 | 61.3333 |
| 2 | 250 | `duration_complete` | 0.0117 | 0.1586 | 0.1931 | 0.1510 | 8.1714 | 0.0760 | 5.2400 | 0.1947 | 62.8000 |
| 3 | 250 | `duration_complete` | -0.0083 | -0.1124 | 0.1798 | 0.1499 | 8.1714 | 0.0760 | 5.2400 | 0.1950 | 62.8000 |
| 4 | 54 | `fall_or_nan` | -0.2903 | -3.9223 | 0.3155 | 0.0814 | 8.2011 | 0.0706 | 5.2334 | 0.2003 | 75.9259 |
| 5 | 250 | `duration_complete` | 0.0110 | 0.1482 | 0.1857 | 0.1467 | 8.1714 | 0.0760 | 5.2400 | 0.1998 | 66.8000 |
| 6 | 250 | `duration_complete` | -0.0259 | -0.3505 | 0.1917 | 0.1554 | 8.1714 | 0.0760 | 5.2400 | 0.1870 | 71.2000 |
| 7 | 250 | `duration_complete` | -0.0277 | -0.3738 | 0.1885 | 0.1541 | 8.1714 | 0.0760 | 5.2400 | 0.1893 | 72.8000 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0181 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.1013 |
| left_hip_pitch | 21.8257 | 0.1471 | 5.2400 | 0.1919 |
| left_knee | 21.8257 | 0.1639 | 5.2400 | 0.2687 |
| left_ankle | 18.5312 | 0.1097 | 4.9191 | 0.2028 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0138 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0080 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0031 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0013 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0253 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0642 |
| right_hip_pitch | 22.4434 | 0.1900 | 4.6448 | 0.1841 |
| right_knee | 15.4427 | 0.3088 | 5.2400 | 0.2535 |
| right_ankle | 14.2073 | 0.0490 | 5.2400 | 0.2046 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
