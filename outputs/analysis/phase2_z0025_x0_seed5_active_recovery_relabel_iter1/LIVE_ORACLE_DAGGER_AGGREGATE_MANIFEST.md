# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`
- `outputs/analysis/phase2_z0025_x0_seed5_active_recovery_relabel_iter1/live_oracle_dagger_x008_manifest.json`
- `outputs/analysis/phase2_z0025_x0_seed5_active_recovery_relabel_iter1/live_oracle_dagger_x0_manifest.json`

## Thresholds

- min_entries: `3`
- min_samples: `1`
- min_mean_vx: `-10.0`
- max_vy_abs_p95: `999.0`
- max_pitch_abs_p95: `999.0`
- min_base_height: `-10.0`
- max_sent_velocity_p95: `999.0`
- max_tracking_p95: `999.0`
- include_source_regex: `None`
- exclude_source_regex: `None`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `16`
- kept_entries: `16`
- rejected_entries: `0`
- samples: `10643`
- source_files: `16`
- max_source_fraction: `0.0625`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_000/trace.jsonl | 750 | 0.0312 | 1.8327 | 0.1586 | 0.1096 | 0.1519 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_001/trace.jsonl | 750 | 0.0352 | 1.8268 | 0.1591 | 0.1164 | 0.1563 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_002/trace.jsonl | 750 | 0.0350 | 1.8553 | 0.1595 | 0.1063 | 0.1512 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_003/trace.jsonl | 750 | 0.0288 | 1.8353 | 0.1570 | 0.1121 | 0.1552 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_004/trace.jsonl | 750 | 0.0347 | 1.8328 | 0.1592 | 0.1103 | 0.1506 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_005/trace.jsonl | 750 | 0.0303 | 1.8159 | 0.1576 | 0.1332 | 0.1464 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_006/trace.jsonl | 750 | 0.0345 | 1.8488 | 0.1581 | 0.1003 | 0.1532 |
| phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_007/trace.jsonl | 750 | 0.0291 | 1.8582 | 0.1587 | 0.1051 | 0.1565 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0005 | 0.2392 | 0.0419 | 0.0189 | 0.1519 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | -0.0002 | 0.2488 | 0.0405 | 0.0275 | 0.1563 |
| rollouts_x0/student/seed_005/trace.jsonl | 43 | -0.3468 | 0.3646 | 0.0503 | 1.3180 | 0.0575 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0211 | 1.3677 | 0.1320 | 0.1260 | 0.1519 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0169 | 1.3636 | 0.1312 | 0.1216 | 0.1555 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0215 | 1.3622 | 0.1304 | 0.1165 | 0.1506 |
| rollouts_x008/student/seed_005/trace.jsonl | 100 | 0.0401 | 1.5603 | 0.1423 | 0.2016 | 0.1464 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0197 | 1.3731 | 0.1324 | 0.1116 | 0.1530 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
