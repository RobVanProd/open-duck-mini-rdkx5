# Physical Start-Pose Calibration Gate

Purpose: prove the real Duck's mechanical home/start pose matches the
sim/runtime pose before interpreting any future robot walking result.

This is a robot-side gate. Do not run it unless the robot is physically
supported and Rob is present. It does not authorize walking, grounded replay, or
policy tests.

## Why This Matters

`BEST_WALK_ONNX_2` and the Open Duck Mini v2 runtime are closed-loop around the
assumption that the robot starts from the same body and joint geometry used in
sim. A small physical mismatch at home can shift foot contact timing, stance
loading, and the first weight transfer enough to make a valid policy fail on
hardware.

The current evidence verifies the software path only partially:

```text
runtime HWI.init_pos == sim scene_flat_terrain.xml home keyframe
home_pose_log_test had small compensated tracking errors
live RDK-X5 duck_config offsets were captured
```

It does not prove the real mechanical leg geometry was re-calibrated to the
documented home/start pose after later robot work. The large live left-knee
offset is the biggest warning:

```text
left_knee offset:  -1.4880 rad
right_knee offset:  0.0798 rad
```

## Expected Runtime Home Pose

These are the commanded compensated joint positions in radians. The sim
`scene_flat_terrain.xml` home keyframe uses the same 14 actuator values.

| index | joint | home rad | live offset rad |
|---:|---|---:|---:|
| 0 | left_hip_yaw | 0.002 | 0.0844 |
| 1 | left_hip_roll | 0.053 | 0.0721 |
| 2 | left_hip_pitch | -0.630 | -0.0890 |
| 3 | left_knee | 1.368 | -1.4880 |
| 4 | left_ankle | -0.784 | -0.0767 |
| 5 | neck_pitch | 0.000 | 0.0245 |
| 6 | head_pitch | 0.000 | 0.0000 |
| 7 | head_yaw | 0.000 | -0.0890 |
| 8 | head_roll | 0.000 | -0.0399 |
| 9 | right_hip_yaw | -0.003 | 0.0951 |
| 10 | right_hip_roll | -0.065 | -0.0476 |
| 11 | right_hip_pitch | 0.635 | 0.0660 |
| 12 | right_knee | 1.379 | 0.0798 |
| 13 | right_ankle | -0.796 | 0.1887 |

## Gate Procedure

1. Support the robot safely with feet visible and no grounded walking load.
2. Command and hold runtime home pose only.
3. Photograph or video front, side-left, side-right, and rear views.
4. Compare physical hip pitch, knee, ankle, and foot geometry against the sim
   home pose, not just against telemetry tracking error.
5. Pay special attention to:
   - left knee angle versus right knee angle
   - ankle symmetry
   - feet expected to be similarly placed relative to the body
   - hip pitch symmetry
   - any link or horn visibly one spline/tooth off
6. If any joint is visibly off, stop and run/audit the soft-offset procedure.
7. If offsets change, capture a new `duck_config.json` snapshot.
8. Re-run `home_pose_log_test` after any offset change.

## Commands

Home pose telemetry after instrumentation deployment:

```bash
cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts

/home/sunrise/duck_env/bin/python sim2real_diagnostics.py home_pose_log_test \
  --onnx_model_path /home/sunrise/BEST_WALK_ONNX_2.onnx \
  --telemetry-path /home/sunrise/duck_logs/home_pose_physical_pose_gate.jsonl \
  --i-understand-this-moves-the-robot
```

Analyze after copying the JSONL back:

```bash
python3 tools/analyze_telemetry_obs.py \
  outputs/first_evidence/<timestamp>/home_pose_physical_pose_gate.jsonl \
  --onnx-model policy/BEST_WALK_ONNX_2.onnx \
  --output outputs/first_evidence/<timestamp>/home_pose_physical_pose_gate_analysis.md
```

Soft-offset procedure from the upstream runtime documentation:

```bash
cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
/home/sunrise/duck_env/bin/python find_soft_offsets.py
```

Only run the soft-offset procedure when Rob is ready to manually place joints at
the desired physical zero. Save the printed offsets before editing
`duck_config.json`.

## Pass Criteria

Pass only if all are true:

```text
- physical leg geometry at commanded home visibly matches the sim/runtime home
- left/right hip pitch, knee, and ankle geometry are symmetric enough to trust
- no obvious horn/link one-tooth offset
- home_pose_log_test still shows small compensated joint tracking errors
- gyro stable and upright accel remains +Z dominant
- no repeated bus read/write errors while holding home
- new duck_config snapshot exists if offsets were changed
```

## Hold Criteria

Hold robot walking validation if any are true:

```text
- left knee geometry does not match the right side at home
- either ankle is visibly over-flexed or under-flexed
- feet are not in the expected home stance relative to the body
- offset values change but no new home_pose_log_test is captured
- telemetry passes but physical geometry is visibly off
```

## Decision Rule

Do not interpret future real-robot walking failure as policy evidence until this
gate passes. If this gate fails, the next work is physical calibration and a new
home-pose evidence packet, not more policy training.
