# Physical Start-Pose Field Sheet

Use this while the robot is supported for the repo soft-offset and home-pose checks.
The primary check is numeric soft-offset calibration; visual home inspection is secondary.
Telemetry alone cannot pass this gate because offsets are applied on both command and readback.

source_joint_map: `/home/lsd/robots/open-duck-mini-rdkx5/docs/joint_map_template.yaml`
gate_doc: `/home/lsd/robots/open-duck-mini-rdkx5/docs/PHYSICAL_START_POSE_CALIBRATION_GATE.md`

## Repo Contract

- `find_soft_offsets.py` sets physical zero by computing `offset = new_pos - current_pos`.
- Runtime writes `servo_goal = command + offset` for the current all-`+1` joint directions.
- Runtime reads `reported_position = servo_present - offset`.
- `zero_pos` is all zeros; `init_pos` below must match the sim `home` keyframe.

## Joint Targets

| idx | joint | side | physical joint | zero checked | home rad | home deg | live offset rad | home checked | notes |
|---:|---|---|---|---|---:|---:|---:|---|---|
| 0 | `left_hip_yaw` | left | hip_yaw | [ ] | 0.0020 | 0.1 | 0.0844 | [ ] | |
| 1 | `left_hip_roll` | left | hip_roll | [ ] | 0.0530 | 3.0 | 0.0721 | [ ] | |
| 2 | `left_hip_pitch` | left | hip_pitch | [ ] | -0.6300 | -36.1 | -0.0890 | [ ] | |
| 3 | `left_knee` | left | knee_pitch | [ ] | 1.3680 | 78.4 | -1.4880 | [ ] | |
| 4 | `left_ankle` | left | ankle_pitch | [ ] | -0.7840 | -44.9 | -0.0767 | [ ] | |
| 5 | `neck_pitch` | center | neck_pitch | [ ] | 0.0000 | 0.0 | 0.0245 | [ ] | |
| 6 | `head_pitch` | center | head_pitch | [ ] | 0.0000 | 0.0 | 0.0000 | [ ] | |
| 7 | `head_yaw` | center | head_yaw | [ ] | 0.0000 | 0.0 | -0.0890 | [ ] | |
| 8 | `head_roll` | center | head_roll | [ ] | 0.0000 | 0.0 | -0.0399 | [ ] | |
| 9 | `right_hip_yaw` | right | hip_yaw | [ ] | -0.0030 | -0.2 | 0.0951 | [ ] | |
| 10 | `right_hip_roll` | right | hip_roll | [ ] | -0.0650 | -3.7 | -0.0476 | [ ] | |
| 11 | `right_hip_pitch` | right | hip_pitch | [ ] | 0.6350 | 36.4 | 0.0660 | [ ] | |
| 12 | `right_knee` | right | knee_pitch | [ ] | 1.3790 | 79.0 | 0.0798 | [ ] | |
| 13 | `right_ankle` | right | ankle_pitch | [ ] | -0.7960 | -45.6 | 0.1887 | [ ] | |

## Soft-Offset Procedure

- [ ] live `duck_config.json` backed up before any calibration
- [ ] `find_soft_offsets.py` run/audited with robot supported
- [ ] printed offsets saved in a log
- [ ] old/new offsets compared before editing `duck_config.json`
- [ ] changed offsets copied into `duck_config.json` only after review

## Secondary Photos / Video

- [ ] front view at home
- [ ] left side view at home
- [ ] right side view at home
- [ ] rear view at home
- [ ] close-up of left knee and ankle
- [ ] close-up of right knee and ankle

## Mechanical Checks

- [ ] left knee geometry matches the expected home bend
- [ ] right knee geometry matches the expected home bend
- [ ] left/right knee geometry is symmetric enough to trust
- [ ] left/right ankle geometry is symmetric enough to trust
- [ ] feet are similarly placed relative to the body
- [ ] no horn/link appears one tooth off
- [ ] no cable strain is pulling a leg away from home

## Telemetry Checks After Any Offset Change

- [ ] new `duck_config.json` snapshot captured
- [ ] `home_pose_log_test` rerun
- [ ] joint tracking errors remain small
- [ ] gyro stable
- [ ] upright accel remains +Z dominant
- [ ] no repeated bus read/write errors while holding home

## Decision

- [ ] PASS: physical home pose matches spec and telemetry passes
- [ ] HOLD: physical pose is off, offsets changed without new telemetry, or left knee remains unexplained
