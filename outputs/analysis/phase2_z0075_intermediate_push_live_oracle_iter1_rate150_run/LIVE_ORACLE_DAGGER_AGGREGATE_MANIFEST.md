# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_curated_aggregate_manifest.json`
- `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_run/live_oracle_dagger_x008_manifest.json`
- `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter1_rate150_run/live_oracle_dagger_x0_manifest.json`

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

- input_entries: `61`
- kept_entries: `61`
- rejected_entries: `0`
- samples: `45501`
- source_files: `57`
- max_source_fraction: `0.0328`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_000/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_001/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_002/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_003/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_004/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_005/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_006/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_007/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 750 | -0.0000 | 0.0410 | 0.0303 | 0.0118 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | -0.0000 | 0.0410 | 0.0303 | 0.0118 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0007 | 0.3442 | 0.0453 | 0.0345 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0007 | 0.3442 | 0.0453 | 0.0345 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0005 | 0.0865 | 0.0349 | 0.0450 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0005 | 0.0865 | 0.0349 | 0.0450 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0106 | 1.1418 | 0.1009 | 0.1156 | 0.1523 |
| relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | -0.0002 | 0.0803 | 0.0368 | 0.0672 | 0.1568 |
| relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0265 | 1.4246 | 0.1371 | 0.1602 | 0.1527 |
| relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 501 | 0.0281 | 1.4498 | 0.1415 | 0.1189 | 0.1566 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | -0.0004 | 0.0584 | 0.0286 | 0.0344 | 0.1528 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | -0.0005 | 0.0952 | 0.0361 | 0.0662 | 0.1568 |
| rollouts_x0/student/seed_002/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_003/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_004/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_005/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_006/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_007/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0223 | 1.3621 | 0.1340 | 0.1819 | 0.1527 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0272 | 1.3721 | 0.1339 | 0.1496 | 0.1568 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
