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

This is not mainly a visual standard. The repo defines a numeric calibration
contract:

```text
runtime/scripts/find_soft_offsets.py
runtime/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py zero_pos
runtime/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py init_pos
Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml home keyframe
```

The soft-offset procedure is the repo-defined way to make physical servo zero
line up with runtime `zero_pos`. Runtime home pose is then `init_pos`, and the
sim home keyframe uses the same 14 actuator values.

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

Compensated telemetry can look good even if the physical zero is wrong, because
the same `joints_offsets` values are used when writing commands and when reading
positions back.

## Repo Calibration Contract

`find_soft_offsets.py` performs the calibration interactively:

```text
1. load HWI with a dummy config
2. set HWI.init_pos = HWI.zero_pos
3. command all joints to software zero
4. for each joint:
   - command software zero again
   - read current servo position
   - disable torque for that joint
   - operator manually moves the joint to desired physical zero
   - read the new servo position
   - compute offset = new_pos - current_pos
   - test moving that joint back to software zero with the offset applied
5. print offsets to copy into duck_config.json
```

Runtime write/read math:

```text
servo_goal = joints_dir[joint] * commanded_position + joints_offsets[joint]
reported_position = joints_dir[joint] * (servo_present_position - joints_offsets[joint])
```

So a correct `duck_config.json` must make this true:

```text
commanded_position = 0.0  -> physical repo-defined zero
commanded_position = init_pos[joint] -> physical sim/runtime home pose
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
2. Back up the live `duck_config.json`.
3. Run/audit the repo soft-offset procedure if physical zero has not been
   recently verified.
4. Compare newly printed offsets against the current live offsets before
   editing `duck_config.json`.
5. If offsets are changed, save the edited config and capture a new config
   snapshot.
6. Command and hold runtime home pose only.
7. Photograph or video front, side-left, side-right, and rear views as a
   secondary mechanical sanity check.
8. Compare physical hip pitch, knee, ankle, and foot geometry against the sim
   home pose, not just against telemetry tracking error.
9. Pay special attention to:
   - left knee angle versus right knee angle
   - ankle symmetry
   - feet expected to be similarly placed relative to the body
   - hip pitch symmetry
   - any link or horn visibly one spline/tooth off
10. Re-run `home_pose_log_test` after any offset change.

Optional field sheet:

```bash
python3 tools/generate_physical_start_pose_sheet.py \
  --output outputs/analysis/PHYSICAL_START_POSE_FIELD_SHEET.md
```

The generated sheet lists home angles in radians/degrees, live offsets, required
photo angles, and checkboxes for the physical inspection.

Optional rendered repo references:

```bash
../envs/open-duck-playground/bin/python tools/render_physical_pose_references.py \
  --output-dir outputs/analysis/physical_pose_references
```

This renders:

```text
zero_contact_sheet.png  # all 14 joints at 0.0 rad; find_soft_offsets.py reference
home_contact_sheet.png  # runtime init_pos / sim home keyframe
```

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

Do not rerun soft-offset calibration just because the offsets are large. If the
commanded runtime home pose visually matches the repo-rendered home reference
and `home_pose_log_test` tracks cleanly, leave offsets unchanged unless a
specific joint mismatch is visible.

Recommended safe wrapper before running the interactive offset script:

```bash
mkdir -p /home/sunrise/duck_logs /home/sunrise/duck_config_backups
cp /home/sunrise/duck_config.json \
  /home/sunrise/duck_config_backups/duck_config.before_start_pose_recalib_$(date -u +%Y%m%dT%H%M%SZ).json

cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
/home/sunrise/duck_env/bin/python find_soft_offsets.py \
  2>&1 | tee /home/sunrise/duck_logs/find_soft_offsets_$(date -u +%Y%m%dT%H%M%SZ).log
```

## Raw Servo Home Offset Audit

The numeric comparison that catches a home-pose offset mismatch is:

```text
sim home keyframe joint angle
vs
raw servo read_present_position while the robot is physically in that same home geometry
```

For each joint:

```text
implied_offset = raw_present_position - joint_dir * sim_home
missing_offset = implied_offset - current_duck_config_offset
```

This is the right comparison only if the robot was physically placed in the
repo-defined home geometry independently of the current offsets. If the runtime
first commanded home using the current `duck_config.json`, the same calculation
mostly re-derives the current configured offset plus tracking error.

Read-only audit command from this repo:

```bash
python3 tools/audit_robot_raw_home_offsets.py \
  --ssh sunrise@192.168.1.50 \
  --identity-file /home/lsd/robots/.duck_access/rdk_key \
  --known-hosts /home/lsd/robots/.duck_access/known_hosts \
  --pose-source physically_aligned_home \
  --output-md outputs/analysis/RAW_HOME_OFFSET_AUDIT.md \
  --output-json outputs/analysis/raw_home_offset_audit.json
```

Safety and interpretation:

```text
- The audit is read-only: no motor command, no torque change, no config edit.
- Run it only when no other bus controller is active.
- Use pose-source=physically_aligned_home only if the robot was manually placed
  in the rendered sim-home geometry, not merely commanded there.
- If the robot was commanded to home first, use pose-source=commanded_home and
  treat the output as a raw/readback sanity check, not a physical-zero proof.
```

## Pass Criteria

Pass only if all are true:

```text
- repo soft-offset procedure has been run/audited or the current offsets are otherwise proven current
- physical zero agrees with repo-defined zero for each leg joint
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
- physical zero has not been re-verified after mechanical work
- newly found offsets differ materially from the live duck_config offsets
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

If the robot holds commanded home, telemetry tracks cleanly, and the physical
home pose matches the repo-rendered `home_contact_sheet.png`, treat start/home
pose mismatch as downranked. Return to gait/control investigation rather than
blindly re-running `find_soft_offsets.py`.
