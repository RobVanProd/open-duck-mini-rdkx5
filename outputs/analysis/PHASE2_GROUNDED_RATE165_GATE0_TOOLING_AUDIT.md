# Grounded Rate165 Gate-0 Tooling Audit

Date: 2026-07-11

Status: `PASS_OFFLINE_TOOLING_READY; ROBOT SNAPSHOT_NOT_CAPTURED`

## Evidence Correction

The hardware approval packet initially described `left_knee=-1.4880 rad` as
live. That was contradicted by stronger, later repository evidence:

- 2026-06-27 operator-recorded correction: `-1.4880 -> 0.0371 rad`;
- post-correction config SHA256:
  `131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b`;
- snapshot:
  `outputs/first_evidence/20260627T213827Z_corrected_knee_refit/20260627T213849Z_rdkx5_config_snapshot.json`;
- supported 0.25/0.5/1.0 Hz tracking passed, with left/right knee tracking p95
  both approximately `0.0078 rad`.

The old value is historical, not current. A fresh supported-home gate remains
required because no current full-pose geometry evidence exists.

## Gate-0 Coverage

`tools/snapshot_robot_config.py` now captures:

- full `duck_config.json`, path, and SHA256;
- `start_paused`, IMU setting/calibration hash, and joint offsets;
- runtime path, Git commit when the runtime is a Git checkout, and dirty flag;
- hashes/presence for telemetry and diagnostic instrumentation;
- an inventory and SHA256 for every root/runtime policy `.onnx` file;
- Python/runtime package versions.

The SSH implementation executes the snapshot source through stdin. It no
longer writes an inline helper under `/tmp`, and a caller-supplied
`--config-path` is now honored remotely.

## Offline Validation

The following passed without SSH, robot access, or GPU use:

```text
python3 -m py_compile tools/snapshot_robot_config.py
PASS_SNAPSHOT_V2_SCHEMA
PASS_SSH_SNAPSHOT_STDIN_NO_REMOTE_WRITE
git diff --check
```

The local schema test confirmed:

```text
schema_version = open_duck_mini_config_snapshot_v2
runtime revision/dirty fields present
policy inventory is a list
instrumentation inventory is a list
```

## Exact Remaining Boundary

Tooling is ready, but no current robot truth has been sampled. Gate 0 still
requires explicit authorization for read-only SSH. Gate 1 separately requires
Rob present, the robot supported, and explicit authorization for the home-pose
command. Neither gate was performed during this audit.
