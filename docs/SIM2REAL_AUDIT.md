# Open Duck Mini Sim-to-Real Audit

Generated: 2026-06-21

Scope: read-only repository inspection plus non-invasive diagnostic plan. No runtime behavior, gains, offsets, policy logic, or robot commands were changed.

## Current Project Status

- Robot bring-up notes in `outputs/duck_rdkx5_status.md` say the RDK-X5 board is accessible, all 14 servos communicate, the Xbox controller is paired, IMU was verified, home pose was reached, and servo zero calibration was completed on 2026-06-14.
- `DUCK_STATUS.md` says the local active candidate is `open_duck_peer/bundle/open_duck_mini_candidate/candidate.onnx`, but this audit focuses on the requested baseline `BEST_WALK_ONNX_2.onnx`.
- Prior walk/probe logs under `outputs/walk_*` are historical. They show unpaused motion, tilt growth/spikes, and repeated servo bus CRC read errors, but they are not synchronized policy telemetry.
- The main unknown remains whether the forward lean comes from policy behavior or from deployed observations/actions differing from the sim contract.

Live RDK-X5 snapshot update, 2026-06-21:

- Current board SSH path is Wi-Fi `sunrise@192.168.1.50`; direct Ethernet `192.168.127.10` is fallback only.
- Snapshot file: `outputs/evidence/20260621T180046Z_rdkx5_config_snapshot.json`.
- Board runtime path: `/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5`.
- Board Python env: `/home/sunrise/duck_env/bin/python`.
- Board policy `/home/sunrise/BEST_WALK_ONNX_2.onnx` SHA256 matches this audit: `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`.
- Board config has `imu_upside_down=true`, `start_paused=true`, `phase_frequency_factor_offset=0.0`.
- No `imu_calib_data.pkl` was found in the snapshot search paths.
- Board runtime files were copied read-only into `outputs/evidence/20260621T180046Z_board_runtime/` for comparison.
- The board runtime is an RDK-X5 fork and is not a git repo. It differs from the local reference runtime:
  - `raw_imu.py` uses an `I2CCompat` layer instead of direct `board`/`busio`.
  - `feet_contacts.py` uses `Hobot.GPIO` on RDK-X5 with BCM pins 22/27.
  - `rustypot_position_hwi.py` has `_retry(..., tries=8)` around bus operations.
  - `rustypot_position_hwi.py` defines `joints_dir = {name: 1.0 for name in self.joints}` and comments that the left knee was physically re-flipped, so no software sign flip is intended.
  - Historical at audit time: the telemetry/instrumentation changes in this
    workspace had not yet been deployed to the board runtime. Superseded by
    deployment evidence in
    `outputs/deployments/20260621T223541Z/DEPLOYMENT_SUMMARY.md`, which
    verifies the opt-in walker telemetry patch and HWI bus counters on the
    board.

## Repo Structure Summary

| Path | Purpose |
| --- | --- |
| `Open_Duck_Mini/` | Main Open Duck Mini repo, bundled pretrained ONNX files, docs, legacy experiments, robot descriptions. |
| `Open_Duck_Mini_Runtime/` | Runtime used on robot. Main hardware policy loop is `scripts/v2_rl_walk_mujoco.py`. |
| `Open_Duck_Playground/` | MuJoCo/JAX training and simulation inference code for Open Duck Mini v2. |
| `Open_Duck_reference_motion_generator/` | Polynomial reference motion generator and robot URDFs. |
| `outputs/` | Prior board status, calibration notes, walk logs, wiggle diagnostics, generated mechanical artifacts. |
| `open_duck_peer/` | Candidate deploy bundle and preflight artifacts. Not the baseline target of this audit. |

## Critical Files

| File | Role |
| --- | --- |
| `Open_Duck_Mini/BEST_WALK_ONNX_2.onnx` | Requested pretrained baseline policy. |
| `Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco.py` | Real robot control loop, observation builder, ONNX inference, action scaling, servo command. |
| `Open_Duck_Mini_Runtime/mini_bdx_runtime/mini_bdx_runtime/onnx_infer.py` | ONNX Runtime wrapper. |
| `Open_Duck_Mini_Runtime/mini_bdx_runtime/mini_bdx_runtime/rustypot_position_hwi.py` | Hardware joint map, home pose, servo position read/write, offsets. |
| `Open_Duck_Mini_Runtime/mini_bdx_runtime/mini_bdx_runtime/raw_imu.py` | Runtime IMU source actually imported by the walking script. |
| `Open_Duck_Mini_Runtime/mini_bdx_runtime/mini_bdx_runtime/duck_config.py` | Runtime JSON config parser for `start_paused`, `imu_upside_down`, `joints_offsets`, phase offset. |
| `Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py` | Training env observation/action definitions and sim control logic. |
| `Open_Duck_Playground/playground/open_duck_mini_v2/mujoco_infer.py` | MuJoCo policy replay path. |
| `Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml` | Sim scene, home keyframe, floor friction. |
| `Open_Duck_Playground/playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml` | Main MJCF robot model, inertials, joints, actuators, sensors. |
| `Open_Duck_Playground/playground/common/export_onnx.py` | ONNX export path, including embedded observation normalization. |

## ONNX Policy Information

Target policy:

```text
Open_Duck_Mini/BEST_WALK_ONNX_2.onnx
SHA256: 3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
Size: 884177 bytes
```

Other related ONNX files found:

| File | SHA256 | I/O |
| --- | --- | --- |
| `Open_Duck_Mini/BEST_WALK_ONNX.onnx` | `cb61453a8bcb547ccfdeb4f03ba0fa67ebcf767dcf4aa6e5c9a0d92b302f9b23` | `obs[1,101] -> continuous_actions[1,14]` |
| `Open_Duck_Playground/ONNX.onnx` | `591e3f51d22e322f3d72d72fce14d8190e7d2e010e49140924fff8b7dc29d23a` | `obs[1,101] -> continuous_actions[1,14]` |
| `open_duck_peer/bundle/open_duck_mini_candidate/candidate.onnx` | `6c90e252c023f405ae8ffe9c81e1c6771c2aee0dcfdd9f9f5081d36224f068ce` | `obs[1,101] -> continuous_actions[1,14]` |

ONNX Runtime metadata for `BEST_WALK_ONNX_2.onnx`:

| Tensor | Name | Shape | Dtype |
| --- | --- | ---: | --- |
| Input | `obs` | `[1, 101]` | `tensor(float)` / float32 |
| Output | `continuous_actions` | `[1, 14]` | `tensor(float)` / float32 |

Loading path:

- `RLWalk.__init__()` creates `OnnxInfer(self.onnx_model_path, awd=True)`.
- `OnnxInfer.__init__()` creates `onnxruntime.InferenceSession(path, providers=["CPUExecutionProvider"])`.
- `OnnxInfer.infer()` with `awd=True` calls `session.run(None, {"obs": [inputs]})` and returns `outputs[0][0]`.

Normalization:

- Observations are normalized inside the ONNX graph, not in runtime Python.
- `Open_Duck_Playground/playground/common/export_onnx.py` exports `(inputs - mean) / std`, then MLP, then `tanh`.
- In `BEST_WALK_ONNX_2.onnx`, the first graph nodes are:
  - `Sub(obs, mlp_13_1/sub/ReadVariableOp:0)`
  - `Mul(..., ConstantFolding/mlp_13_1/truediv_recip:0)`
- Embedded mean initializer:
  - `mlp_13_1/sub/ReadVariableOp:0`, shape `(101,)`, float32.
- Embedded reciprocal std initializer:
  - `ConstantFolding/mlp_13_1/truediv_recip:0`, shape `(101,)`, float32.
- First 20 means for `BEST_WALK_ONNX_2`: `[0.00128, -0.00829, 0.00092, -0.03789, -0.07972, 9.49014, -0.00053, 0.00034, -0.00104, 0.34302, -0.00036, -0.00059, -0.00128, -0.00118, -0.00974, -0.11066, 0.02038, 0.12295, 0.12726, -0.04679]`.
- First 20 reciprocal std values: `[1.35111, 1.14837, 1.41218, 0.49739, 0.34798, 0.30221, 12.0445, 9.08235, 1.81156, 2.43416, 2.33475, 1.21367, 3.64464, 16.4985, 14.13375, 11.90191, 9.8896, 11.91341, 12.88819, 12.69803]`.

Output semantics:

- Output is 14 normalized action values after `tanh`, so nominal range is `[-1, 1]`.
- Runtime interprets output as position target offsets:
  - `motor_targets = init_pos + action * action_scale`
  - default `action_scale = 0.25` rad.
- These are PD/position targets, not torques.
- Runtime applies a target slew limit:
  - `max_motor_velocity = 5.24 rad/s`
  - at 50 Hz, max target change is `0.1048 rad/tick`.
- Optional low-pass filtering is available only if CLI `--cutoff_frequency` is set.
- No explicit action clipping to joint limits was found in the real runtime; only the velocity clamp is applied.

## Observation Vector Breakdown

Total observation length: 101.

| Indices | Count | Name | Runtime source | Units/scaling |
| --- | ---: | --- | --- | --- |
| `0:3` | 3 | `gyro` | `raw_imu.Imu.get_data()["gyro"]` | Expected rad/s from BNO055 driver; not scaled in Python. Verify on Pi. |
| `3:6` | 3 | `accelero` | `raw_imu.Imu.get_data()["accelero"]` | Expected m/s^2 from BNO055 driver; not scaled in Python. |
| `6:13` | 7 | `commands` | `last_commands` | `[x_vel, y_vel, yaw_vel, neck_pitch, head_pitch, head_yaw, head_roll]`; velocities in m/s or rad/s command space, head in rad. |
| `13:27` | 14 | `dof_pos_error` | `hwi.get_present_positions() - init_pos` | radians. |
| `27:41` | 14 | `dof_vel_scaled` | `hwi.get_present_velocities() * 0.05` | rad/s times `0.05`. |
| `41:55` | 14 | `last_action` | previous policy output | normalized action units, before `action_scale`. |
| `55:69` | 14 | `last_last_action` | action history | normalized action units. |
| `69:83` | 14 | `last_last_last_action` | action history | normalized action units. |
| `83:97` | 14 | `motor_targets` | last absolute motor targets | radians, absolute joint command targets after scaling/rate limit/head overlay. |
| `97:99` | 2 | `feet_contacts` | GPIO feet contact sensors | booleans, left then right. |
| `99:101` | 2 | `imitation_phase` | polynomial reference phase | `[cos(phase), sin(phase)]`. |

Per-index expanded map:

| Index | Field |
| ---: | --- |
| 0 | gyro_x |
| 1 | gyro_y |
| 2 | gyro_z |
| 3 | accel_x |
| 4 | accel_y |
| 5 | accel_z |
| 6 | command_x_velocity |
| 7 | command_y_velocity |
| 8 | command_yaw_velocity |
| 9 | command_neck_pitch |
| 10 | command_head_pitch |
| 11 | command_head_yaw |
| 12 | command_head_roll |
| 13-26 | joint position error for action joints 0-13, in action order |
| 27-40 | joint velocity for action joints 0-13, scaled by 0.05 |
| 41-54 | previous action for action joints 0-13 |
| 55-68 | action from two ticks ago for action joints 0-13 |
| 69-82 | action from three ticks ago for action joints 0-13 |
| 83-96 | previous absolute motor target for action joints 0-13 |
| 97 | left foot contact |
| 98 | right foot contact |
| 99 | imitation_phase_cos |
| 100 | imitation_phase_sin |

Observation contents confirmed:

- Previous actions: yes, three 14-value history blocks.
- Gait phase / clock input: yes, `imitation_phase` cos/sin.
- Command velocity: yes, first three command entries.
- Head command inputs: yes, command entries 3-6.
- IMU values: yes, gyro and accelerometer.
- History buffers: yes, action history only. No joint/IMU history in real runtime.
- Projected gravity/quaternion/RPY: no, not in this runtime path.

Potential phase mismatch:

- Training `Joystick.step()` increments `imitation_phase` before `_get_obs()`.
- MuJoCo inference also increments phase before `get_obs()`.
- Real `RLWalk.run()` calls `get_obs()` first, then increments `imitation_phase`, then runs inference.
- This likely makes real phase one policy tick behind sim inference/training after startup.

## Action Vector Breakdown

Action order follows `HWI.joints` order and the MuJoCo actuator order.

Runtime equation:

```python
target_rad[i] = init_pos[i] + action[i] * action_scale
```

Default `action_scale` is `0.25` rad. At `action=+1`, target is home plus `+0.25 rad`; at `action=-1`, target is home minus `0.25 rad`, before rate limiting and optional filtering.

| Action index | Joint | Servo ID | Home/init rad | Sim ctrl range rad | Output unit | Hardware command unit | Explicit sign flip |
| ---: | --- | ---: | ---: | --- | --- | --- | --- |
| 0 | left_hip_yaw | 20 | 0.002 | `[-0.523599, 0.523599]` | normalized action | radians | no |
| 1 | left_hip_roll | 21 | 0.053 | `[-0.436332, 0.436332]` | normalized action | radians | no |
| 2 | left_hip_pitch | 22 | -0.630 | `[-1.221730, 0.523599]` | normalized action | radians | no |
| 3 | left_knee | 23 | 1.368 | `[-1.570796, 1.570796]` | normalized action | radians | no |
| 4 | left_ankle | 24 | -0.784 | `[-1.570796, 1.570796]` | normalized action | radians | no |
| 5 | neck_pitch | 30 | 0.000 | `[-0.349066, 1.134464]` | normalized action | radians | no |
| 6 | head_pitch | 31 | 0.000 | `[-0.785398, 0.785398]` | normalized action | radians | no |
| 7 | head_yaw | 32 | 0.000 | `[-2.792527, 2.792527]` | normalized action | radians | no |
| 8 | head_roll | 33 | 0.000 | `[-0.523599, 0.523599]` | normalized action | radians | no |
| 9 | right_hip_yaw | 10 | -0.003 | `[-0.523599, 0.523599]` | normalized action | radians | no |
| 10 | right_hip_roll | 11 | -0.065 | `[-0.436332, 0.436332]` | normalized action | radians | no |
| 11 | right_hip_pitch | 12 | 0.635 | `[-0.523599, 1.221730]` | normalized action | radians | no |
| 12 | right_knee | 13 | 1.379 | `[-1.570796, 1.570796]` | normalized action | radians | no |
| 13 | right_ankle | 14 | -0.796 | `[-1.570796, 1.570796]` | normalized action | radians | no |

Important action-path notes:

- Hardware offsets are added in `HWI.set_position_all()` as `position + joints_offsets[joint]`.
- Local workstation `~/duck_config.json` has all offsets `0.0`.
- Live RDK-X5 `~/duck_config.json` was read on 2026-06-21 and stored in `outputs/evidence/20260621T180046Z_rdkx5_config_snapshot.json`.
- `rustypot` was not installed in this local environment, so the exact low-level radians-to-packet conversion could not be inspected. Verify `rustypot==0.1.0` on the robot.

## Control Loop Timing

Real runtime:

| Item | Value | Source |
| --- | --- | --- |
| Main loop file | `Open_Duck_Mini_Runtime/scripts/v2_rl_walk_mujoco.py` | `RLWalk.run()` |
| Default control frequency | 50 Hz | CLI `--control_freq`, default `50` |
| Control dt | 0.02 s | `1 / control_freq` |
| ONNX inference frequency | nominal 50 Hz | one inference per unpaused tick when obs is valid |
| Servo command frequency | nominal 50 Hz | one `hwi.set_position_all()` per tick |
| Servo feedback read frequency | nominal 50 Hz | positions and velocities read every `get_obs()` |
| IMU worker frequency | `control_freq`, default 50 Hz | `raw_imu.Imu(sampling_freq=int(control_freq))` |
| Controller command frequency | 20 Hz | `self.command_freq = 20` |
| Sim dt | 0.002 s | `Joystick.default_config().sim_dt` / `MJInferBase.sim_dt` |
| Sim control dt | 0.02 s | `ctrl_dt=0.02`; sim inference decimation 10 |
| Sim action repeat | 1 | `Joystick.default_config().action_repeat` |

Decimation and held commands:

- Real runtime has no explicit action decimation beyond one policy inference per tick.
- Gamepad commands update at 20 Hz and are held between controller thread updates.
- Servo targets are held by servo hardware between writes.
- Sim inference steps MuJoCo every 0.002 s and runs policy every 10 sim steps.

Filters and smoothing:

- Action target rate limit is always active in the current runtime file.
- Optional `LowPassActionFilter` is only active when `--cutoff_frequency` is provided.
- No IMU low-pass filter is active in `raw_imu.py`.
- `raw_imu` queue is maxsize 1 and `get_data()` returns the last sample if the queue is empty.

Watchdog/safety:

- Optional `--max_runtime_seconds` stops the loop.
- Gamepad A toggles pause.
- `finally` cleanup calls `hwi.turn_off()` and stops optional devices.
- Loop prints if policy control budget is exceeded.
- No fall detector or tilt watchdog was found in the stock runtime path.

## Joint Mapping

| Policy index | Joint name | Servo ID | Side | Physical joint | Explicit sign flip | Zero offset source | Min/max command | Home pose | Units | Read feedback |
| ---: | --- | ---: | --- | --- | --- | --- | --- | ---: | --- | --- |
| 0 | left_hip_yaw | 20 | left | hip yaw | no | `duck_config.joints_offsets` | sim `[-0.523599, 0.523599]`; runtime not clipped | 0.002 | rad | yes, `read_present_position` |
| 1 | left_hip_roll | 21 | left | hip roll | no | same | sim `[-0.436332, 0.436332]`; runtime not clipped | 0.053 | rad | yes |
| 2 | left_hip_pitch | 22 | left | hip pitch | no | same | sim `[-1.221730, 0.523599]`; runtime not clipped | -0.630 | rad | yes |
| 3 | left_knee | 23 | left | knee pitch | no | same | sim `[-1.570796, 1.570796]`; runtime not clipped | 1.368 | rad | yes |
| 4 | left_ankle | 24 | left | ankle pitch | no | same | sim `[-1.570796, 1.570796]`; runtime not clipped | -0.784 | rad | yes |
| 5 | neck_pitch | 30 | center | neck pitch | no | same | sim `[-0.349066, 1.134464]`; runtime not clipped | 0.000 | rad | yes |
| 6 | head_pitch | 31 | center | head pitch | no | same | sim `[-0.785398, 0.785398]`; runtime not clipped | 0.000 | rad | yes |
| 7 | head_yaw | 32 | center | head yaw | no | same | sim `[-2.792527, 2.792527]`; runtime not clipped | 0.000 | rad | yes |
| 8 | head_roll | 33 | center | head roll | no | same | sim `[-0.523599, 0.523599]`; runtime not clipped | 0.000 | rad | yes |
| 9 | right_hip_yaw | 10 | right | hip yaw | no | same | sim `[-0.523599, 0.523599]`; runtime not clipped | -0.003 | rad | yes |
| 10 | right_hip_roll | 11 | right | hip roll | no | same | sim `[-0.436332, 0.436332]`; runtime not clipped | -0.065 | rad | yes |
| 11 | right_hip_pitch | 12 | right | hip pitch | no | same | sim `[-0.523599, 1.221730]`; runtime not clipped | 0.635 | rad | yes |
| 12 | right_knee | 13 | right | knee pitch | no | same | sim `[-1.570796, 1.570796]`; runtime not clipped | 1.379 | rad | yes |
| 13 | right_ankle | 14 | right | ankle pitch | no | same | sim `[-1.570796, 1.570796]`; runtime not clipped | -0.796 | rad | yes |

Live board zero offsets from `outputs/evidence/20260621T180046Z_rdkx5_config_snapshot.json`:

| Policy index | Joint name | Servo ID | Live `joints_offsets` rad |
| ---: | --- | ---: | ---: |
| 0 | left_hip_yaw | 20 | 0.0844 |
| 1 | left_hip_roll | 21 | 0.0721 |
| 2 | left_hip_pitch | 22 | -0.0890 |
| 3 | left_knee | 23 | -1.4880 |
| 4 | left_ankle | 24 | -0.0767 |
| 5 | neck_pitch | 30 | 0.0245 |
| 6 | head_pitch | 31 | 0.0000 |
| 7 | head_yaw | 32 | -0.0890 |
| 8 | head_roll | 33 | -0.0399 |
| 9 | right_hip_yaw | 10 | 0.0951 |
| 10 | right_hip_roll | 11 | -0.0476 |
| 11 | right_hip_pitch | 12 | 0.0660 |
| 12 | right_knee | 13 | 0.0798 |
| 13 | right_ankle | 14 | 0.1887 |

Conversion on write:

```python
ids_positions = {
    self.joints[joint]: position + self.joints_offsets[joint]
    for joint, position in joints_positions.items()
}
self.io.write_goal_position(list(self.joints.values()), list(ids_positions.values()))
```

Conversion on read:

```python
present_positions = [
    pos - self.joints_offsets[joint]
    for joint, pos in zip(self.joints.keys(), present_positions)
]
```

Notes:

- Python code assumes `rustypot` read/write positions are radians.
- Exact servo packet units are UNKNOWN from this workstation because `rustypot` is not installed here.
- Physical positive movement direction per joint is not documented in code. It must be verified by `joint_identity_test`.

## IMU Frame and Sign Processing

Runtime IMU source actually used:

- `v2_rl_walk_mujoco.py` imports `Imu` from `mini_bdx_runtime.raw_imu`, not `mini_bdx_runtime.imu`.
- Sensor library: `adafruit_bno055`.
- Device mode in `raw_imu.py`: `adafruit_bno055.NDOF_MODE`.
- Transport: I2C using `busio.I2C(board.SCL, board.SDA)`.

Axis remap:

| Config | Axis remap tuple |
| --- | --- |
| `imu_upside_down=true` | `(Y, X, Z, NEGATIVE, NEGATIVE, NEGATIVE)` |
| `imu_upside_down=false` | `(Y, X, Z, NEGATIVE, POSITIVE, POSITIVE)` |

Local workstation config:

- `~/duck_config.json` has `imu_upside_down=false`.

Live RDK-X5 config:

- `outputs/evidence/20260621T180046Z_rdkx5_config_snapshot.json` confirms the board config uses `imu_upside_down=true`.
- Therefore the board runtime uses BNO055 axis remap `(Y, X, Z, NEGATIVE, NEGATIVE, NEGATIVE)`.

Values passed to ONNX:

| ONNX indices | Runtime value | Units | Processing |
| --- | --- | --- | --- |
| `0:3` | `gyro` | expected rad/s | raw BNO055 driver value after BNO055 axis remap |
| `3:6` | `accelero` | expected m/s^2 | raw BNO055 acceleration after axis remap, with `accelero[0] -= x_offset` |

Filtering/calibration:

- No explicit low-pass filtering.
- `x_offset` exists but defaults to `0`; `tare_x()` is not called in `raw_imu.py`.
- `user_pitch_bias` is accepted by `raw_imu.Imu.__init__()` but not used.
- If `imu_calib_data.pkl` exists in the working directory, BNO055 accelerometer/gyro/magnetometer offsets are loaded.
- If no calibration pickle exists, runtime prints that IMU is uncalibrated and continues.

Important mismatch to test:

- MuJoCo inference `mujoco_infer.py` mutates `accelerometer[0] += 1.3` before observation construction.
- Training `joystick.py` has `accelerometer.at[0].set(accelerometer[0] + 1.3)` without assignment, which likely has no effect in JAX.
- Real runtime does not add `+1.3`; it subtracts only `x_offset`, which remains `0` unless manually tared in modified code.
- Prior board logs show ad hoc wrappers doing an x-offset tare, but stock `raw_imu.py` does not.

No roll/pitch/yaw:

- The policy does not receive RPY, quaternion, or projected gravity in the real runtime.
- The separate `imu.py` computes quaternion/Euler, but it is not imported by `v2_rl_walk_mujoco.py`.

## Home Pose and Calibration

Runtime home pose is `HWI.init_pos`:

```text
left_hip_yaw      0.002
left_hip_roll     0.053
left_hip_pitch   -0.630
left_knee         1.368
left_ankle       -0.784
neck_pitch        0.000
head_pitch        0.000
head_yaw          0.000
head_roll         0.000
right_hip_yaw    -0.003
right_hip_roll   -0.065
right_hip_pitch   0.635
right_knee        1.379
right_ankle      -0.796
```

Sim default pose:

- `scene_flat_terrain.xml` `keyframe name="home"` has identical actuator ctrl vector and qpos joint vector for the 14 actuators.
- Therefore local runtime home pose matches the sim default actuator pose.

Calibration offsets:

- Stored in `duck_config.json` under `joints_offsets`.
- Local workstation config has all offsets `0.0`.
- Live RDK-X5 config was copied into `outputs/evidence/20260621T180046Z_rdkx5_config_snapshot.json`; the exact offsets are listed in the joint mapping section above and in `docs/joint_map_template.yaml`.

Zeroing procedure:

- `scripts/find_soft_offsets.py` moves robot to zero, disables each joint, asks the user to manually set desired zero, computes `offset = new_pos - current_pos`, and prints offsets for `duck_config.json`.
- `scripts/configure_motor.py` sets motor ID, mode, P/I/D, acceleration, then commands position `0`.

Manual offsets:

- Local visible config has no manual hip/knee/ankle offsets.
- Live board config confirms a large `left_knee` offset of `-1.4880 rad`; this should be treated as real calibration evidence, but joint identity must still verify physical direction and readback behavior.

## Sim Model Assumptions

Primary sim files:

- `Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain.xml`
- `Open_Duck_Playground/playground/open_duck_mini_v2/xmls/open_duck_mini_v2.xml`
- `Open_Duck_Playground/playground/open_duck_mini_v2/xmls/open_duck_mini_v2_backlash.xml`
- `Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml`
- `Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml`
- `Open_Duck_Mini/mini_bdx/robots/open_duck_mini_v2/robot.urdf`
- `Open_Duck_reference_motion_generator/open_duck_reference_motion_generator/robots/open_duck_mini/open_duck_mini.urdf`

MuJoCo model summary from `scene_flat_terrain.xml`:

| Item | Value |
| --- | --- |
| `nq` | 21 |
| `nv` | 20 |
| `nu` | 14 |
| `njnt` | 15 |
| sim timestep | 0.002 s |
| control dt | 0.02 s |
| decimation | 10 sim ticks per policy tick in inference |
| root subtree mass | 2.1071407 kg at `trunk_assembly` |
| floor friction | `0.6 0.005 0.0001`, `condim=3` |
| foot collision geoms | `left_foot_bottom_tpu`, `right_foot_bottom_tpu` |
| foot geom friction | `1.0 0.005 0.0001`, `condim=3` |
| IMU site | `site name="imu" pos="-0.08 -0.0 0.05"` under `base` |

Actuator defaults from `open_duck_mini_v2.xml`:

| Parameter | Value |
| --- | --- |
| actuator type | position actuator |
| class | `sts3215` |
| `kp` | 13.37 |
| `kv` | 0.0 |
| `forcerange` | `[-3.23, 3.23]` |
| joint damping | 0.56 |
| joint frictionloss | 0.068 |
| joint armature | 0.027 |

Training config from `joystick.py`:

| Parameter | Value |
| --- | --- |
| `ctrl_dt` | 0.02 |
| `sim_dt` | 0.002 |
| `episode_length` | 1000 |
| `action_repeat` | 1 |
| `action_scale` | 0.25 |
| `dof_vel_scale` | 0.05 |
| `max_motor_velocity` | 5.24 rad/s |
| action delay randomization | min 0, max 3 env steps |
| IMU delay randomization | min 0, max 3 env steps |
| command x range | `[-0.15, 0.15]` |
| command y range | `[-0.2, 0.2]` |
| yaw command range | `[-1.0, 1.0]` |

Link masses and inertial positions from MuJoCo model:

| Body | Mass kg | Inertial pos |
| --- | ---: | --- |
| trunk_assembly | 0.698526 | `[-0.048326, -0.000100, 0.038497]` |
| hip_roll_assembly | 0.066480 | `[0.000795, -0.000005, -0.033060]` |
| left_roll_to_pitch_assembly | 0.075160 | `[0.050804, -0.000411, 0.020470]` |
| knee_and_ankle_assembly | 0.124070 | `[0.002534, -0.039064, 0.010278]` |
| knee_and_ankle_assembly_2 | 0.072590 | `[0.000005, -0.057746, 0.018114]` |
| foot_assembly | 0.075240 | `[0.011072, -0.024661, 0.019063]` |
| neck_pitch_assembly | 0.066180 | `[-0.000006, 0.049297, 0.018179]` |
| head_pitch_to_yaw | 0.016938 | `[-0.007662, 0.026015, 0.018668]` |
| neck_yaw_assembly | 0.091810 | `[0.004129, 0.000004, -0.022283]` |
| head_assembly | 0.406607 | `[0.008154, -0.003908, 0.022773]` |
| hip_roll_assembly_2 | 0.066480 | `[0.000795, -0.000005, -0.033060]` |
| right_roll_to_pitch_assembly | 0.075160 | `[-0.050804, -0.000421, 0.020470]` |
| knee_and_ankle_assembly_3 | 0.124070 | `[0.002534, 0.039064, 0.010809]` |
| knee_and_ankle_assembly_4 | 0.072590 | `[0.000005, -0.057746, 0.018114]` |
| foot_assembly_2 | 0.075240 | `[0.011072, -0.024661, 0.019063]` |

## Hardware Deployment Path

ONNX output to servo packet:

```text
policy.infer(obs)
  -> action[14], normalized tanh output
  -> last action history updated
  -> motor_targets = init_pos + action * action_scale
  -> motor_targets rate-limited by max_motor_velocity/control_freq
  -> optional low-pass filter if --cutoff_frequency is set
  -> prev_motor_targets updated
  -> head command overlay: motor_targets[5:9] += last_commands[3:7]
  -> make_action_dict(motor_targets, hwi.joints.keys())
  -> HWI.set_position_all()
  -> position + joints_offsets[joint]
  -> rustypot.feetech.write_goal_position(ids, positions)
```

Sensor feedback to ONNX input:

```text
BNO055 gyro/accel in raw_imu worker
  -> latest queued imu_data
  -> HWI.read_present_position(all servo ids)
  -> subtract joints_offsets
  -> HWI.read_present_velocity(all servo ids)
  -> FeetContacts GPIO read
  -> concatenate 101-value obs
  -> ONNX graph internal normalization
  -> MLP/tanh continuous_actions
```

## Existing Logging

Found logging:

- `--save_obs` in `v2_rl_walk_mujoco.py` pickles `robot_saved_obs.pkl`.
- `mujoco_infer.py` pickles `mujoco_saved_obs.pkl` only on KeyboardInterrupt.
- Existing `outputs/walk_*` wrappers log 1 Hz-ish tilt/gyro/accel/cmd and lifecycle messages.
- `scripts/check_voltage.py` prints per-servo voltage.
- `scripts/check_motors.py` reads positions and can move each motor by 0.1 rad.
- `outputs/joint_wiggle_20260615_234130/*.log` captured target/readback for joint-pair wiggles.

Logging gaps:

- No synchronized per-control-tick log of raw observation, normalized-policy input, action, scaled target, command target, actual joint feedback, and joint tracking error.
- No timestamp on every observation/action pair in stock runtime.
- No captured ONNX normalization output.
- No battery voltage in policy run logs.
- No servo bus error count per tick.
- No fall/safety state in stock runtime.
- No raw board `duck_config.json` snapshot in the current workspace.

## Minimal Telemetry Logger Proposal

Record JSONL or CSV every tick, or every N ticks for lower overhead. JSONL is preferred because the observation/action vectors are fixed but large.

Required fields:

- `timestamp_monotonic`
- `timestamp_wall`
- `tick`
- `dt`
- `control_freq`
- `paused`
- `raw_imu.gyro`
- `raw_imu.accelero`
- `policy_imu.gyro`
- `policy_imu.accelero`
- `commands`
- `feet_contacts`
- `imitation_i`
- `imitation_phase`
- `raw_observation`
- `observation_mean` and `observation_std_recip` or model hash reference
- `onnx_action`
- `action_scale`
- `scaled_action_delta`
- `motor_targets_pre_clip`
- `motor_targets_post_rate_limit`
- `motor_targets_post_filter`
- `motor_targets_sent`
- `actual_joint_positions`
- `actual_joint_velocities`
- `joint_tracking_error`
- `joints_offsets`
- `servo_ids`
- `battery_voltage_by_servo` if available
- `servo_bus_errors` if available
- `fall_or_safety_state` if available

## Diagnostic Test Scripts Needed

1. `home_pose_log_test`
   - Hold home pose for 10 seconds and log all telemetry fields.
   - Purpose: prove home pose, IMU steady-state channels, offsets, and joint tracking.

2. `imu_tilt_test`
   - No policy movement. User manually tilts forward/back/left/right.
   - Purpose: map raw IMU channels to physical pitch/roll and policy observation indices.

3. `joint_identity_test`
   - Move each joint by a tiny safe delta one at a time, then return.
   - Purpose: verify index -> joint -> servo ID -> physical direction truth table.

4. `suspended_policy_replay`
   - Run `BEST_WALK_ONNX_2` with feet off ground/support stand, log at control frequency.
   - Purpose: inspect action sequence and tracking without ground contact dynamics.

5. `grounded_policy_replay`
   - Run on floor with logging until fall or manual stop.
   - Purpose: capture the forward lean failure with full observation/action/joint context.

6. `actuator_sine_sweep`
   - Small sine sweeps on hip pitch, knee, ankle pitch.
   - Purpose: measure target vs actual tracking, latency, saturation, and asymmetry.

See `docs/diagnostic_test_plan.md` for details.

## Suspected Failure Points for Forward Lean

Ranked from most likely to inspect first:

1. IMU accelerometer frame/offset mismatch.
   - Policy receives accel, not RPY.
   - Live board uses `imu_upside_down=true`; local workstation guard config uses `false`, so workstation config must not be treated as hardware truth.
   - MuJoCo inference has an accel-x `+1.3` mutation, training likely does not, real runtime does not.
   - Prior logs show nonzero upright accel x/y values and tilt estimates changing around unpause.

2. Live joint offsets are asymmetric and need physical verification.
   - Live `~/duck_config.json` is now captured in `outputs/evidence/20260621T180046Z_rdkx5_config_snapshot.json`.
   - The `left_knee` offset is `-1.4880 rad`, while `right_knee` is `0.0798 rad`.
   - This may be correct after mechanical repair/calibration, but it makes `joint_identity_test` and home-pose tracking logs mandatory before walking.

3. Servo bus CRC/read errors causing stale or corrupted joint state.
   - Prior walk logs contain repeated `read crc` mismatch lines.
   - If `get_present_positions()` or velocities intermittently fail, the runtime skips a tick; if stale values slip through, observation quality degrades.

4. Phase timing mismatch.
   - Real policy sees the previous `imitation_phase` compared with sim inference/training. Likely small, but easy to log and compare.

5. Actuator tracking mismatch under load.
   - Sim assumes position actuator `kp=13.37`, force range `+-3.23`.
   - Runtime sets servo P coefficient `30` by default, with head KPs lowered.
   - Physical tracking under ground contact is not logged at policy tick rate.

6. Joint sign/identity still needs a complete truth table.
   - Code has no explicit sign flips.
   - Prior mechanical fixes make this less likely, but the only safe proof is a per-joint identity test with video/log.

7. Foot contact mismatch.
   - Policy observes left/right foot contact booleans.
   - RDK-X5 logs warn about GPIO pull-ups; contact correctness under walking is unproven.

## Recommended Next Steps

1. Use the live board snapshot `outputs/evidence/20260621T180046Z_rdkx5_config_snapshot.json` as the calibration evidence baseline.
2. Deploy the non-invasive telemetry/logger files to the board runtime path without changing behavior by default.
3. Run tests in this order:
   - `home_pose_log_test`
   - `imu_tilt_test`
   - `joint_identity_test`
   - `suspended_policy_replay`
   - push test
   - `grounded_policy_replay`
   - `actuator_sine_sweep`
4. For the failing grounded replay, capture side-view video and synchronized JSONL/CSV logs.
5. Do not tune gains, offsets, or training until the truth table proves which channel is wrong.

## Unknowns and Required Follow-up

| Unknown | Why unknown | Next file/function/action |
| --- | --- | --- |
| Exact `rustypot` radians-to-packet conversion | Package not installed locally | Inspect `rustypot==0.1.0` on board or install in matching env. |
| BNO055 runtime units from installed driver | Driver package not installed locally | Inspect `adafruit_bno055` on board; confirm gyro rad/s and accel m/s^2. |
| Physical positive direction per joint | Code has names but not physical motion direction | Run `joint_identity_test` with video/log. |
| Actual servo voltage/current/load during policy | Stock runtime does not log these | Add telemetry reads if supported by `rustypot`; otherwise use `pypot`/separate voltage script. |
| Contact sensor polarity under real walking | Code assumes `not pin.value` means contact | Log `feet_contacts` during manual lift/touch and walking. |
| Whether `BEST_WALK_ONNX_2` itself produces forward-leaning targets in suspension | No synchronized action log exists | Run `suspended_policy_replay`. |
