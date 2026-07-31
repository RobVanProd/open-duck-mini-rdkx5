# Reference Action Envelope

status: `HOLD_REFERENCE_EXCEEDS_ACTION_ENVELOPE`
reference: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/reference_motion_x004_override.pkl`
reference_sha256: `deb8553d72e162331e788ca2b7e3e055b765a2ae01642b15ae316f07afb55601`
command: `{'x': 0.04, 'y': 0.0, 'yaw': 0.0}`
period_steps: `27`
action_scale: `0.25`
max_motor_velocity_rad_s: `5.24`

## Closest Phases To Home

| phase | home_distance_rad | saturated_joint_count | max_abs_action |
|---:|---:|---:|---:|
| 5 | 0.2851 | 0 | 0.7420 |
| 19 | 0.2855 | 0 | 0.6625 |
| 6 | 0.2893 | 0 | 0.7367 |
| 20 | 0.3431 | 0 | 0.7313 |
| 18 | 0.3467 | 0 | 0.6805 |
| 25 | 0.3589 | 0 | 0.9269 |
| 7 | 0.3663 | 0 | 0.9447 |
| 11 | 0.3730 | 0 | 0.9447 |

## Per Joint

| joint | max_abs_action | action_sat_pct | target_vel_p95 | target_vel_max |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0525 | 0.0000 | 0.1428 | 0.1441 |
| left_hip_roll | 0.5290 | 0.0000 | 1.3358 | 1.3472 |
| left_hip_pitch | 1.5774 | 22.2222 | 4.6386 | 5.1496 |
| left_knee | 1.7088 | 14.8148 | 8.0846 | 8.6417 |
| left_ankle | 1.1908 | 11.1111 | 3.8951 | 4.2828 |
| neck_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| head_pitch | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| head_yaw | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| head_roll | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| right_hip_yaw | 0.0576 | 0.0000 | 0.1340 | 0.1456 |
| right_hip_roll | 0.5230 | 0.0000 | 1.3450 | 1.3576 |
| right_hip_pitch | 1.9062 | 18.5185 | 5.4889 | 6.0116 |
| right_knee | 2.2704 | 14.8148 | 9.8963 | 13.2122 |
| right_ankle | 1.0817 | 7.4074 | 4.8676 | 7.6140 |

## Interpretation

- This is a kinematic/action-contract audit, not a sim rollout.
- `max_abs_action > 1` means the raw reference target exceeds `home + action * action_scale`.
- Target velocity above `max_motor_velocity_rad_s` means the target cannot be followed without slew limiting.
- If this holds, behavior cloning from raw reference joint positions would train against an out-of-envelope target.
