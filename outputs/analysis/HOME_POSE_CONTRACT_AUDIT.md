# Home Pose Contract Audit

status: `PASS_HOME_POSE_CONTRACT`
tolerance_rad: `1e-09`

This is an offline source/config audit. It does not SSH, command motors,
deploy files, edit `duck_config.json`, or run a policy.

## Summary

- max_abs_runtime_minus_sim_home_rad: `0.0000`
- max_abs_runtime_zero_rad: `0.0000`
- max_abs_raw_bypass_minus_normal_home_rad: `1.4880`
- home_mismatch_joints: `[]`
- zero_mismatch_joints: `[]`

## Interpretation

- Runtime `init_pos` matches sim `home` if `runtime_minus_sim_home_rad` is near zero.
- Runtime raw home command is `joint_dir * sim_home + config_offset`.
- Raw-bypass home command is just `joint_dir * sim_home`; it ignores offsets and is not a safe calibration shortcut.

## Joint Table

| idx | joint | id | runtime home | sim home | diff | offset | normal raw home | raw-bypass home | bypass-normal |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `left_hip_yaw` | 20 | 0.0020 | 0.0020 | 0.0000 | 0.0844 | 0.0864 | 0.0020 | -0.0844 |
| 1 | `left_hip_roll` | 21 | 0.0530 | 0.0530 | 0.0000 | 0.0721 | 0.1251 | 0.0530 | -0.0721 |
| 2 | `left_hip_pitch` | 22 | -0.6300 | -0.6300 | 0.0000 | -0.0890 | -0.7190 | -0.6300 | 0.0890 |
| 3 | `left_knee` | 23 | 1.3680 | 1.3680 | 0.0000 | -1.4880 | -0.1200 | 1.3680 | 1.4880 |
| 4 | `left_ankle` | 24 | -0.7840 | -0.7840 | 0.0000 | -0.0767 | -0.8607 | -0.7840 | 0.0767 |
| 5 | `neck_pitch` | 30 | 0.0000 | 0.0000 | 0.0000 | 0.0245 | 0.0245 | 0.0000 | -0.0245 |
| 6 | `head_pitch` | 31 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 7 | `head_yaw` | 32 | 0.0000 | 0.0000 | 0.0000 | -0.0890 | -0.0890 | 0.0000 | 0.0890 |
| 8 | `head_roll` | 33 | 0.0000 | 0.0000 | 0.0000 | -0.0399 | -0.0399 | 0.0000 | 0.0399 |
| 9 | `right_hip_yaw` | 10 | -0.0030 | -0.0030 | 0.0000 | 0.0951 | 0.0921 | -0.0030 | -0.0951 |
| 10 | `right_hip_roll` | 11 | -0.0650 | -0.0650 | 0.0000 | -0.0476 | -0.1126 | -0.0650 | 0.0476 |
| 11 | `right_hip_pitch` | 12 | 0.6350 | 0.6350 | 0.0000 | 0.0660 | 0.7010 | 0.6350 | -0.0660 |
| 12 | `right_knee` | 13 | 1.3790 | 1.3790 | 0.0000 | 0.0798 | 1.4588 | 1.3790 | -0.0798 |
| 13 | `right_ankle` | 14 | -0.7960 | -0.7960 | 0.0000 | 0.1887 | -0.6073 | -0.7960 | -0.1887 |

## Decision

This audit can prove the source-level sim/runtime home contract. It
cannot prove that the physical robot was freshly calibrated to that
contract. Physical proof still requires either the repo
`find_soft_offsets.py` procedure or a read-only raw-position audit while
the robot is independently placed in the repo-defined home geometry.

Do not command raw-bypass sim home. Use the runtime compensated home
command or the read-only raw audit instead.
