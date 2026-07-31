# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x008_manifest.json`
- `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0/live_oracle_dagger_x0_manifest.json`

## Thresholds

- min_entries: `11`
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

- input_entries: `18`
- kept_entries: `18`
- rejected_entries: `0`
- samples: `12806`
- source_files: `18`
- max_source_fraction: `0.0556`

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
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0005 | 0.2325 | 0.0416 | 0.0169 | 0.1527 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0001 | 0.2223 | 0.0400 | 0.0414 | 0.1565 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0295 | 1.8374 | 0.1573 | 0.1375 | 0.1527 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0345 | 1.8062 | 0.1587 | 0.1229 | 0.1565 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0345 | 1.8445 | 0.1596 | 0.1279 | 0.1514 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0264 | 1.8436 | 0.1558 | 0.1419 | 0.1559 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0346 | 1.8547 | 0.1603 | 0.1356 | 0.1508 |
| rollouts_x008/student/seed_005/trace.jsonl | 56 | -0.2654 | 1.3626 | 0.1000 | 1.2936 | 0.0677 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0333 | 1.8298 | 0.1577 | 0.1161 | 0.1533 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0287 | 1.8468 | 0.1574 | 0.1171 | 0.1564 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
