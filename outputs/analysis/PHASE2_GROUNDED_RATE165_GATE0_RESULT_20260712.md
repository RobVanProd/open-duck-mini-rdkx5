# Grounded Rate165 Gate-0 Result

Date: 2026-07-12

Status: `PASS_GATE0_SNAPSHOT_WITH_CLOCK_WARNING`

Authorization: read-only SSH snapshot only. Motors were not imported, enabled,
or commanded. No runtime, policy, deployment, or configuration write occurred.

## Authoritative Snapshot

```text
outputs/first_evidence/20260712T050249Z_grounded_rate165_gate0_clock_provenance/
  20260712T050250Z_rdkx5_config_snapshot.json
snapshot SHA256: af433893c47ee03ecca45854f0c66af692865e04e2ab7888e100b844e278bcf0
trusted collector UTC: 2026-07-12T05:02:49.464451+00:00
```

## Live State

```text
duck_config SHA256: 131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b
start_paused: true
imu_upside_down: true
phase_frequency_factor_offset: 0.0
left_knee offset: 0.0371 rad
right_knee offset: 0.0798 rad
baseline policy SHA256: 3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
```

The full live config is byte-identical by SHA256 and structurally identical to
the post-correction 2026-06-27 snapshot. The corrected knee state persists.

Policies present on the board:

```text
BEST_WALK_ONNX_2.onnx
  3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067
corrected_bridge_cmd_conditioned_rate175_20260627.onnx
  63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e
```

The grounded rate165 candidate is not staged, as required at Gate 0.

## Instrumentation Identity

All three live hashes match their canonical repository copies:

```text
telemetry.py
  64419dc23e36f79a3f652030a1db43b7f3ae414da3a11cdfb770fd0cc0a1e162
sim2real_diagnostics.py
  d2e8df200fae773ed2c45200da9b67ab1e809db537d5cb93756c73bece1cd33b
v2_rl_walk_auto.py
  4582b277ebd01a7331bd7d6ff1049e8e71c006656bef6b56cf75120dbd93a269
```

The live runtime directory is not a Git checkout, so `runtime_git_commit` and
dirty state are unavailable. File hashes are the available revision evidence.

## Clock Finding

The board reported:

```text
remote UTC: 2000-01-01T00:00:58.789664+00:00
offset from trusted collector: -837147710.7 s
remote_clock_plausible: false
```

This is a real boot-time clock/provenance warning. Snapshot tooling now records
the workstation `collector_utc` before SSH and uses it for Gate-0 freshness;
the untrusted board clock is retained separately rather than silently treated
as current time. No clock-setting command was authorized or run.

## Other Observations

- no separate IMU calibration pickle was found; this is unchanged from the
  June 27 snapshot;
- ONNX Runtime is `1.18.1` in the robot environment;
- the RDK-X5 reports Linux `6.1.83-aarch64`;
- Gate 0 did not read servo state or import motor-control modules.

## Decision Boundary

Gate 0 is complete. Gate 1 remains unapproved and would command supported home
pose, so it must not run under this authorization. The board-clock warning
should be retained in every subsequent evidence packet; fixing the clock is a
separate system write and was not inferred from permission to read.
