# Deployment Notes

These notes are for deploying the additive diagnostic instrumentation from this repository to the live RDK-X5 board.

## Current Board Access

Use Wi-Fi first:

```bash
ssh -i /home/lsd/robots/.duck_access/rdk_key \
  -o UserKnownHostsFile=/home/lsd/robots/.duck_access/known_hosts \
  -o StrictHostKeyChecking=no \
  sunrise@192.168.1.50
```

Direct Ethernet `192.168.127.10` is fallback only when a cable is connected.

## Runtime Paths

```text
Board runtime: /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5
Board Python:  /home/sunrise/duck_env/bin/python
Policy:        /home/sunrise/BEST_WALK_ONNX_2.onnx
Config:        /home/sunrise/duck_config.json
Logs:          /home/sunrise/duck_logs
```

## Additive Files

Deploy these files into the board runtime:

```text
instrumentation/mini_bdx_runtime/telemetry.py
instrumentation/scripts/sim2real_diagnostics.py
```

Target paths:

```text
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/mini_bdx_runtime/mini_bdx_runtime/telemetry.py
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts/sim2real_diagnostics.py
```

## Required Runtime Patch For Policy Replay Telemetry

`sim2real_diagnostics.py suspended_policy_replay` expects `v2_rl_walk_mujoco.RLWalk` to accept telemetry arguments. The live board file does not yet include that patch.

Before patching `v2_rl_walk_mujoco.py`, make a dated backup:

```bash
ssh -i /home/lsd/robots/.duck_access/rdk_key \
  -o UserKnownHostsFile=/home/lsd/robots/.duck_access/known_hosts \
  -o StrictHostKeyChecking=no \
  sunrise@192.168.1.50 \
  'cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts && cp v2_rl_walk_mujoco.py v2_rl_walk_mujoco.py.backup_$(date -u +%Y%m%dT%H%M%SZ)'
```

Do not replace the RDK fork with the local upstream reference file. Preserve:

- RDK-X5 compatibility imports
- existing controller behavior
- servo-bus retry behavior
- `joints_dir` behavior

## First Smoke Checks

These are non-moving checks:

```bash
ssh -i /home/lsd/robots/.duck_access/rdk_key \
  -o UserKnownHostsFile=/home/lsd/robots/.duck_access/known_hosts \
  -o StrictHostKeyChecking=no \
  sunrise@192.168.1.50 \
  'cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts && /home/sunrise/duck_env/bin/python sim2real_diagnostics.py --help'
```

Snapshot from workstation:

```bash
python3 tools/snapshot_robot_config.py \
  --ssh sunrise@192.168.1.50 \
  --identity-file /home/lsd/robots/.duck_access/rdk_key \
  --known-hosts /home/lsd/robots/.duck_access/known_hosts \
  --strict-host-key-checking no
```

## Moving Tests

Do not run moving tests unless the robot is physically supported and the operator is ready to cut power.

Example home-pose log command:

```bash
cd /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5/scripts
/home/sunrise/duck_env/bin/python sim2real_diagnostics.py home_pose_log_test \
  --onnx_model_path /home/sunrise/BEST_WALK_ONNX_2.onnx \
  --telemetry-path /home/sunrise/duck_logs/home_pose_log_test.jsonl \
  --i-understand-this-moves-the-robot
```

Stop after home pose if upright accel, gyro, joint tracking, foot contacts, or bus errors look wrong.
