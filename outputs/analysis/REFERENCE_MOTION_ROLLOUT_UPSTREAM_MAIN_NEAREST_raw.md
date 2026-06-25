# Reference Motion Rollout

status: `HOLD_REFERENCE_TARGET_TERMINATES`
command_x: `0.074`
duration_s: `5.0`
reference: `None`
reference_target_mode: `raw`
first_reference_phase: `1`

## Aggregate

- runs: `8`
- falls: `4`
- duration_complete: `4`
- track_ratio_mean: `-1.1668`
- vx_mean: `-0.0863`
- samples_mean: `147.2500`
- vy_abs_p95_mean: `0.4424`
- action_saturation_pct_mean: `8.1906`
- reference_target_clip_p95_mean: `0.0741`
- joint_tracking_p95_mean: `0.1957`
- reference_contact_mismatch_pct_mean: `70.9015`

## Per Seed

| seed | samples | termination | vx_mean | track_ratio | vy_abs_p95 | base_height_min | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 | contact_mismatch_pct |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 250 | `duration_complete` | -0.0124 | -0.1676 | 0.2300 | 0.1534 | 8.1714 | 0.0760 | 5.2400 | 0.1840 | 72.8000 |
| 1 | 34 | `fall_or_nan` | -0.0925 | -1.2497 | 1.1201 | 0.0949 | 7.9832 | 0.0706 | 5.2400 | 0.2092 | 76.4706 |
| 2 | 250 | `duration_complete` | -0.0089 | -0.1206 | 0.2205 | 0.1526 | 8.1714 | 0.0760 | 5.2400 | 0.1851 | 72.4000 |
| 3 | 250 | `duration_complete` | -0.0199 | -0.2685 | 0.2206 | 0.1564 | 8.1714 | 0.0760 | 5.2400 | 0.1846 | 72.4000 |
| 4 | 52 | `fall_or_nan` | -0.3034 | -4.1001 | 0.2157 | 0.0648 | 8.1044 | 0.0656 | 5.1072 | 0.1981 | 57.6923 |
| 5 | 56 | `fall_or_nan` | -0.2459 | -3.3230 | 0.3056 | 0.0820 | 8.4184 | 0.0777 | 5.2400 | 0.2139 | 66.0714 |
| 6 | 250 | `duration_complete` | -0.0193 | -0.2607 | 0.2112 | 0.1570 | 8.1714 | 0.0760 | 5.2400 | 0.1869 | 71.6000 |
| 7 | 36 | `fall_or_nan` | 0.0115 | 0.1556 | 1.0151 | 0.1031 | 8.3333 | 0.0749 | 5.2400 | 0.2037 | 77.7778 |

## Per Joint

| joint | action_sat_pct | target_clip_p95 | sent_vel_p95 | joint_track_p95 |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0000 | 0.0000 | 0.1143 | 0.0132 |
| left_hip_roll | 0.0000 | 0.0000 | 1.6428 | 0.1019 |
| left_hip_pitch | 21.3922 | 0.1471 | 5.2400 | 0.1820 |
| left_knee | 21.5620 | 0.1639 | 5.2400 | 0.2872 |
| left_ankle | 18.5059 | 0.1097 | 4.9191 | 0.2040 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0097 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0085 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0028 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0013 |
| right_hip_yaw | 0.0000 | 0.0000 | 0.1130 | 0.0138 |
| right_hip_roll | 0.0000 | 0.0000 | 1.6291 | 0.0861 |
| right_hip_pitch | 22.9202 | 0.1900 | 4.6448 | 0.1723 |
| right_knee | 15.8744 | 0.3088 | 5.2400 | 0.2693 |
| right_ankle | 14.2615 | 0.0490 | 5.2400 | 0.2129 |

## Interpretation

- This rollout replaces the ONNX policy with reference-derived actions.
- It still respects action scale and the motor target rate limiter.
- `cycle_projected` mode scales each joint's reference cycle to fit the action and target-rate envelope.
- `contact_gated_projected` additionally damps a swing-leg target if that foot is still loaded in the sim.
- `contact_synchronized_projected` retimes the projected reference phase toward the current simulated contact pattern.
- A pass would show that the matched reference is dynamically trackable in the sim contract.
- A hold means behavior cloning must account for the target/action contract, phase, or contact dynamics before PPO.
