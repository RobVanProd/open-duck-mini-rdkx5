# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.04`
duration_s: `5.0`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`
reference_target_mode: `contact_gated_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `7`
- duration_complete: `1`
- track_ratio_mean: `0.0288`
- vx_mean: `0.0012`
- samples_mean: `105.5000`
- vy_abs_p95_mean: `0.3960`
- action_saturation_pct_mean: `0.4059`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1274`
- reference_contact_mismatch_pct_mean: `69.4217`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 85 | `fall_or_nan` | 0.0078 | 0.1953 | 0.0897 | 0.1535 | 0.2521 | 0.0000 | 2.1972 | 0.1201 | 65.8824 |
| 1 | 29 | `fall_or_nan` | -0.0124 | -0.3096 | 1.2353 | 0.0820 | 0.4926 | 0.0000 | 2.6270 | 0.1346 | 79.3103 |
| 2 | 140 | `fall_or_nan` | 0.0077 | 0.1934 | 0.1115 | 0.1527 | 0.2551 | 0.0000 | 2.3040 | 0.1217 | 62.8571 |
| 3 | 70 | `fall_or_nan` | -0.0132 | -0.3311 | 0.1654 | 0.1562 | 0.3061 | 0.0000 | 2.3490 | 0.1186 | 70.0000 |
| 4 | 168 | `fall_or_nan` | 0.0079 | 0.1975 | 0.0921 | 0.1518 | 0.2976 | 0.0000 | 2.3649 | 0.1189 | 66.6667 |
| 5 | 250 | `duration_complete` | 0.0092 | 0.2291 | 0.0961 | 0.1471 | 0.3429 | 0.0000 | 2.3640 | 0.1218 | 62.8000 |
| 6 | 70 | `fall_or_nan` | -0.0107 | -0.2668 | 0.2534 | 0.1573 | 0.4082 | 0.0000 | 2.5107 | 0.1319 | 72.8571 |
| 7 | 32 | `fall_or_nan` | 0.0129 | 0.3227 | 1.1247 | 0.1007 | 0.8929 | 0.0000 | 3.3228 | 0.1513 | 75.0000 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1429 | 0.0139 |
| left_hip_roll | 0.0000 | 0.0000 | 1.3472 | 0.0803 |
| left_hip_pitch | 0.2370 | 0.0000 | 2.5824 | 0.0952 |
| left_knee | 0.2370 | 0.0000 | 3.9636 | 0.2212 |
| left_ankle | 3.6730 | 0.0000 | 5.1384 | 0.1652 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0132 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0067 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0014 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0010 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.2034 | 0.0197 |
| right_hip_roll | 0.0000 | 0.0000 | 1.3576 | 0.0734 |
| right_hip_pitch | 0.5924 | 0.0000 | 1.6900 | 0.0647 |
| right_knee | 0.0000 | 0.0000 | 2.7071 | 0.1403 |
| right_ankle | 0.0000 | 0.0000 | 3.6445 | 0.1391 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
