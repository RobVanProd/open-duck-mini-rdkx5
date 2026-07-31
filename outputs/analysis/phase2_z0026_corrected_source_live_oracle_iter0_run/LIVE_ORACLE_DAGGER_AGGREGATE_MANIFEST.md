# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json`
- `outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_run/live_oracle_dagger_x008_manifest.json`
- `outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter0_run/live_oracle_dagger_x0_manifest.json`

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
- samples: `13500`
- source_files: `18`
- max_source_fraction: `0.0556`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_000/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_001/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_002/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_003/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_004/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_005/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_006/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_007/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0007 | 0.3442 | 0.0453 | 0.0345 | 0.1523 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0007 | 0.3442 | 0.0453 | 0.0345 | 0.1523 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
