# Evidence Manifest

## Live Snapshot

`evidence/20260621T180046Z_rdkx5_config_snapshot.json`

Captured from `sunrise@192.168.1.50`.

Important fields:

```text
hostname: ubuntu
runtime_path: /home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5
python_env_path: /home/sunrise/duck_env/bin/python
onnx_policy_path: /home/sunrise/BEST_WALK_ONNX_2.onnx
onnx_policy_sha256: 3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
imu_upside_down: true
start_paused: true
phase_frequency_factor_offset: 0.0
imu_calib_data_path: null
```

## Live Config

`evidence/duck_config_20260621T180046Z.json`

SHA256:

```text
087868f8178598f49a2ab4eab1c77b73ed8cd3af33174c543119cb016d69e9e9
```

Notable offsets:

```text
left_knee: -1.4880 rad
right_knee: 0.0798 rad
left_ankle: -0.0767 rad
right_ankle: 0.1887 rad
```

## Policy

`policy/BEST_WALK_ONNX_2.onnx`

SHA256:

```text
3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
```

This matches the board policy snapshot.

## Board Runtime

`runtime/`

Copied from:

```text
/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5
```

This board runtime is an RDK-X5 fork and is not a git repository on the board.

Notable differences from the local reference runtime:

- RDK I2C compatibility layer for IMU.
- RDK GPIO support for foot contacts.
- Servo-bus retry wrapper in HWI.
- `joints_dir` all `+1.0`, with comments saying the left knee was physically re-flipped.

## First Evidence Packet

Expected local packet directory:

```text
outputs/first_evidence/<timestamp>/
```

Expected packet files:

```text
<timestamp>_rdkx5_config_snapshot.json
home_pose_log_test.jsonl
home_pose_analysis.md
imu_tilt_test.jsonl
imu_tilt_analysis.md
foot_contact_test.jsonl
foot_contact_summary.md
```

Expected generated summary:

```text
outputs/analysis/FIRST_EVIDENCE_SUMMARY.md
```

Commit small summaries only when they support a project decision. Keep raw
JSONL logs, videos, and ad hoc hardware outputs outside git unless they are
explicitly reviewed and reduced to a safe excerpt.

## Suspended Replay Evidence

Expected files for zero-command suspended replay:

```text
outputs/first_evidence/<timestamp>/suspended_policy_replay_x0.jsonl
outputs/first_evidence/<timestamp>/suspended_policy_replay_x0_terminal.log
outputs/first_evidence/<timestamp>/suspended_policy_replay_x0_gate.md
outputs/first_evidence/<timestamp>/suspended_policy_replay_x0_warnings.md
```

Expected files for optional `x=0.08` suspended replay:

```text
outputs/first_evidence/<timestamp>/suspended_policy_replay_x008.jsonl
outputs/first_evidence/<timestamp>/suspended_policy_replay_x008_terminal.log
outputs/first_evidence/<timestamp>/suspended_policy_replay_x008_gate.md
outputs/first_evidence/<timestamp>/suspended_policy_replay_x008_warnings.md
```

Do not run `x=0.08` unless the `x=0.0` gate summary recommends `PASS_X0`
or `WARN_PROCEED_WITH_CAUTION`. Nonzero CRC/read retries are a warning, not an
automatic hold, unless they correlate with dt spikes, action saturation or
target jumps, post-startup tracking spikes, repeated write failures, visible
twitching, or a bus-error burst.
Terminal logs are intentionally part of the evidence because servo CRC/read
warnings may be printed before they are exposed as telemetry counters.

## Instrumentation Deployment

Expected local deployment evidence:

```text
outputs/deployments/<timestamp>/DEPLOYMENT_SUMMARY.md
outputs/deployments/<timestamp>/import_check.txt
outputs/deployments/<timestamp>/sim2real_diagnostics_help.txt
outputs/deployments/<timestamp>/v2_rl_walk_mujoco_help.txt
```

Expected board backup path:

```text
/home/sunrise/duck_backups/<timestamp>/
```

Deployment evidence should record:

```text
SSH target
board runtime path
board backup path
copied file paths
source SHA256 hashes
destination SHA256 hashes
non-moving validation commands
runtime telemetry contract status
```

Commit `DEPLOYMENT_SUMMARY.md` only when it is small and useful for a project
decision. Do not commit private SSH material, raw telemetry logs, or videos.

## Excluded

The following are intentionally not committed:

```text
/home/lsd/robots/.duck_access/rdk_key
/home/lsd/robots/.duck_access/known_hosts
raw telemetry JSONL logs
videos
large ad hoc run outputs
```
