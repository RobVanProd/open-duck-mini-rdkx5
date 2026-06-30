# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `d8498b665c201936`
- entries: `8`
- samples: `6000`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0312 | 0.3894 | 1.8327 | 0.1586 | 0.1096 | 0.1519 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0352 | 0.4396 | 1.8268 | 0.1591 | 0.1164 | 0.1563 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0350 | 0.4377 | 1.8553 | 0.1595 | 0.1063 | 0.1512 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0288 | 0.3602 | 1.8353 | 0.1570 | 0.1121 | 0.1552 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0347 | 0.4337 | 1.8328 | 0.1592 | 0.1103 | 0.1506 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_005/trace.jsonl | 0-749 | 750 | `True` | 0.0303 | 0.3794 | 1.8159 | 0.1576 | 0.1332 | 0.1464 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0345 | 0.4317 | 1.8488 | 0.1581 | 0.1003 | 0.1532 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0291 | 0.3632 | 1.8582 | 0.1587 | 0.1051 | 0.1565 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
