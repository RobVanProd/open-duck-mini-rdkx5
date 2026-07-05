# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_command_gated_zero0020_bc_manifest.json`
- `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter1/live_oracle_dagger_x008_manifest.json`
- `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter1/live_oracle_dagger_x0_manifest.json`

## Thresholds

- min_entries: `5`
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

- input_entries: `14`
- kept_entries: `14`
- rejected_entries: `0`
- samples: `10413`
- source_files: `9`
- max_source_fraction: `0.1429`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0008 | 0.0060 | 0.0351 | 0.0638 | 0.1614 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0009 | 0.0066 | 0.0347 | 0.0673 | 0.1609 |
| rollouts_x008/student/seed_000/trace.jsonl | 663 | -0.0018 | 1.4326 | 0.1386 | 0.2192 | 0.0636 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | -0.0011 | 1.4281 | 0.1370 | 0.2037 | 0.0737 |
| seed_000/trace.jsonl | 750 | 0.0008 | 0.0000 | 0.0349 | 0.0633 | 0.1614 |
| seed_000/trace.jsonl | 750 | 0.0272 | 1.4505 | 0.1402 | 0.1737 | 0.1581 |
| seed_001/trace.jsonl | 750 | 0.0254 | 1.4478 | 0.1417 | 0.1876 | 0.1581 |
| seed_001/trace.jsonl | 750 | 0.0009 | 0.0000 | 0.0346 | 0.0667 | 0.1609 |
| seed_002/trace.jsonl | 750 | 0.0008 | 0.0000 | 0.0346 | 0.0647 | 0.1614 |
| seed_002/trace.jsonl | 750 | 0.0269 | 1.4433 | 0.1409 | 0.1894 | 0.1581 |
| seed_006/trace.jsonl | 750 | 0.0232 | 1.4399 | 0.1405 | 0.1917 | 0.1581 |
| seed_006/trace.jsonl | 750 | 0.0007 | 0.0000 | 0.0367 | 0.0699 | 0.1611 |
| seed_007/trace.jsonl | 750 | 0.0265 | 1.4524 | 0.1411 | 0.1724 | 0.1581 |
| seed_007/trace.jsonl | 750 | 0.0009 | 0.0000 | 0.0341 | 0.0657 | 0.1613 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
