# Open Duck Mini Sim-To-Real Diagnostics

Purpose: collect evidence before changing training, offsets, gains, IMU remaps, friction, or action scaling.

Run these on the RDK-X5 unless a command explicitly uses `--ssh`.

Current board runtime path:

```text
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5
```

Current board Python environment:

```text
/home/sunrise/duck_env
```

The diagnostic mode commands below assume the instrumentation files from this
workspace have been deployed to that board runtime path. The snapshot command
can run over SSH from this workstation and does not require deployment.

## Safety

- Any moving test must be run with the robot supported unless the test name says grounded.
- Keep fingers clear of joints and linkages.
- Be ready to cut power.
- Moving tests require `--i-understand-this-moves-the-robot`.
- Default movement amplitudes are intentionally small.
- Prefer JSONL logs in `outputs/telemetry/`.

## 1. Snapshot Live Config

From this workstation, use the current Wi-Fi SSH path first:

```bash
python3 tools/snapshot_robot_config.py \
  --ssh sunrise@192.168.1.50 \
  --identity-file /home/lsd/robots/.duck_access/rdk_key \
  --known-hosts /home/lsd/robots/.duck_access/known_hosts \
  --strict-host-key-checking no
```

Direct Ethernet is retired for normal use. Only use this fallback if a cable is
connected directly to the board and Wi-Fi is not reachable:

```bash
python3 tools/snapshot_robot_config.py \
  --ssh sunrise@192.168.127.10 \
  --identity-file /home/lsd/robots/.duck_access/rdk_key \
  --known-hosts /home/lsd/robots/.duck_access/known_hosts \
  --strict-host-key-checking no
```

The canonical SSH note is [outputs/rdk_x5_ssh_access.md](../outputs/rdk_x5_ssh_access.md).

On the robot itself:

```bash
python3 tools/snapshot_robot_config.py
```

Output:

```text
outputs/evidence/<timestamp>_rdkx5_config_snapshot.json
```

## 2. Extract ONNX Observation Normalization

```bash
python3 tools/extract_onnx_obs_norm.py Open_Duck_Mini/BEST_WALK_ONNX_2.onnx \
  --save-json outputs/evidence/best_walk_onnx_2_obs_norm.json
```

This prints the first six gyro/accel normalization constants and z-score formulas.

## 3. Home Pose Log Test

Robot must be supported. This moves/holds home pose and logs for 10 seconds.

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py home_pose_log_test \
  --onnx_model_path ~/BEST_WALK_ONNX_2.onnx \
  --telemetry-path ~/duck_logs/home_pose_log_test.jsonl \
  --i-understand-this-moves-the-robot
```

Analyze:

```bash
python3 tools/analyze_telemetry_obs.py home_pose_log_test.jsonl \
  --output home_pose_log_test_analysis.md
```

Pass checks:

- `obs[3:6]` upright accel is near ONNX expected accel.
- Joint tracking errors are small.
- No repeated bus read/write errors.
- Feet contact values make sense.

## 4. IMU Tilt Test

No commanded movement. Manually move through:

```text
upright, nose forward, upright, nose backward, upright, left, upright, right
```

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py imu_tilt_test \
  --onnx_model_path ~/BEST_WALK_ONNX_2.onnx \
  --telemetry-path ~/duck_logs/imu_tilt_test.jsonl \
  --duration 35
```

Use `--read-joints` if you also want a full 101-value observation vector during tilt.

Analyze:

```bash
python3 tools/analyze_telemetry_obs.py imu_tilt_test.jsonl \
  --output imu_tilt_test_analysis.md
```

Pass checks:

- Nose forward and nose backward affect opposite signs on the expected accel axis.
- Left/right tilt affects the expected lateral axis.
- Upright accel resembles ONNX normalization mean neighborhood.

## 5. Foot Contact Test

No commanded movement. Manually lift/touch each foot.

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py foot_contact_test \
  --telemetry-path ~/duck_logs/foot_contact_test.jsonl \
  --duration 20
```

Check printed contact booleans and raw GPIO values for left/right polarity.

## 6. Joint Identity Test

Robot must be supported. Each joint moves `+0.03 rad`, `-0.03 rad`, then returns home.

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py joint_identity_test \
  --telemetry-path ~/duck_logs/joint_identity_test.jsonl \
  --summary-path ~/duck_logs/joint_identity_test_summary.json \
  --i-understand-this-moves-the-robot
```

While watching/videoing, fill the `visual_positive_direction` fields afterward.

## 7. Suspended Policy Replay

Robot must be suspended with feet free. Policy starts paused and waits for Enter.

First, zero forward command:

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py suspended_policy_replay \
  --onnx_model_path ~/BEST_WALK_ONNX_2.onnx \
  --telemetry-path ~/duck_logs/suspended_policy_replay_x0.jsonl \
  --command-x 0.0 \
  --duration 15 \
  --i-understand-this-moves-the-robot
```

Only if safe, repeat with `0.08 m/s`:

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py suspended_policy_replay \
  --onnx_model_path ~/BEST_WALK_ONNX_2.onnx \
  --telemetry-path ~/duck_logs/suspended_policy_replay_x008.jsonl \
  --command-x 0.08 \
  --duration 15 \
  --i-understand-this-moves-the-robot
```

## 8. Grounded Policy Replay

Grounded test. Start paused, begin side-view video, then press Enter.

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py grounded_policy_replay \
  --onnx_model_path ~/BEST_WALK_ONNX_2.onnx \
  --telemetry-path ~/duck_logs/grounded_policy_replay.jsonl \
  --command-x 0.0 \
  --duration 10 \
  --i-understand-this-moves-the-robot
```

Stop immediately on fall, large lean, slipping, or asymmetry.

## 9. Actuator Sine Sweep

Robot must be supported. Policy disabled. Default amplitude is `0.03 rad`.

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python sim2real_diagnostics.py actuator_sine_sweep \
  --telemetry-path ~/duck_logs/actuator_sine_sweep.jsonl \
  --i-understand-this-moves-the-robot
```

## Normal Walker With Telemetry

Default behavior is unchanged unless `--log-telemetry` or `--telemetry-path` is used.

```bash
cd ~/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
~/duck_env/bin/python v2_rl_walk_mujoco.py \
  --onnx_model_path ~/BEST_WALK_ONNX_2.onnx \
  --log-telemetry \
  --telemetry-path ~/duck_logs/rl_walk_telemetry.jsonl
```

Add `--telemetry-read-voltage` only when extra servo voltage bus reads are acceptable.

## Files To Send First

```text
outputs/evidence/*_rdkx5_config_snapshot.json
home_pose_log_test.jsonl
home_pose_log_test_analysis.md
imu_tilt_test.jsonl
imu_tilt_test_analysis.md
foot_contact_test.jsonl or summary
joint_identity_test_summary.json
suspended_policy_replay_x0.jsonl
```
