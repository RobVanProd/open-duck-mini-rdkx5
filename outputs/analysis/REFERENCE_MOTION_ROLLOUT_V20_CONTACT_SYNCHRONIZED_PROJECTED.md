# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.04`
duration_s: `5.0`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`
reference_target_mode: `contact_synchronized_projected`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `7`
- duration_complete: `1`
- track_ratio_mean: `-0.3788`
- vx_mean: `-0.0152`
- samples_mean: `120.3750`
- vy_abs_p95_mean: `0.3867`
- action_saturation_pct_mean: `0.9142`
- reference_target_clip_p95_mean: `0.0000`
- joint_tracking_p95_mean: `0.1059`
- reference_contact_mismatch_pct_mean: `7.7531`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 91 | `fall_or_nan` | 0.0078 | 0.1953 | 0.1006 | 0.1559 | 0.7849 | 0.0000 | 3.3214 | 0.0864 | 1.0989 |
| 1 | 31 | `fall_or_nan` | -0.1310 | -3.2758 | 1.1039 | 0.1031 | 0.9217 | 0.0000 | 3.8049 | 0.1508 | 19.3548 |
| 2 | 168 | `fall_or_nan` | 0.0079 | 0.1982 | 0.0852 | 0.1527 | 0.6803 | 0.0000 | 3.3259 | 0.0810 | 2.9762 |
| 3 | 70 | `fall_or_nan` | -0.0106 | -0.2646 | 0.1475 | 0.1595 | 0.8163 | 0.0000 | 3.3259 | 0.0939 | 8.5714 |
| 4 | 245 | `fall_or_nan` | 0.0079 | 0.1973 | 0.0855 | 0.1518 | 0.7289 | 0.0000 | 2.8451 | 0.0796 | 0.4082 |
| 5 | 250 | `duration_complete` | 0.0095 | 0.2370 | 0.0909 | 0.1471 | 0.7714 | 0.0000 | 3.3259 | 0.0840 | 3.6000 |
| 6 | 70 | `fall_or_nan` | -0.0041 | -0.1013 | 0.2598 | 0.1585 | 0.9184 | 0.0000 | 3.9357 | 0.1279 | 12.8571 |
| 7 | 38 | `fall_or_nan` | -0.0087 | -0.2163 | 1.2204 | 0.0646 | 1.6917 | 0.0000 | 3.8228 | 0.1439 | 13.1579 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.5454 | 0.0133 |
| left_hip_roll | 0.0000 | 0.0000 | 1.3641 | 0.0929 |
| left_hip_pitch | 0.7269 | 0.0000 | 5.2400 | 0.0972 |
| left_knee | 0.7269 | 0.0000 | 4.4877 | 0.1432 |
| left_ankle | 8.8266 | 0.0000 | 5.2400 | 0.1151 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0149 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0072 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0018 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0011 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.7227 | 0.0129 |
| right_hip_roll | 0.0000 | 0.0000 | 1.3576 | 0.0923 |
| right_hip_pitch | 0.9346 | 0.0000 | 2.8451 | 0.0869 |
| right_knee | 0.0000 | 0.0000 | 2.9282 | 0.1051 |
| right_ankle | 0.0000 | 0.0000 | 4.3501 | 0.1064 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
