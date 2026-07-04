# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_z0075_iter14_gain095_seed0_pass_merged_manifest.json`

## Thresholds

- min_entries: `1`
- min_samples: `1`
- min_mean_vx: `0.015`
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

- input_entries: `88`
- kept_entries: `51`
- rejected_entries: `37`
- samples: `32073`
- source_files: `46`
- max_source_fraction: `0.0392`

### Rejection Reasons

| reason | count |
|---|---:|
| `low_mean_vx` | 37 |

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
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0272 | 1.4433 | 0.1388 | 0.1324 | 0.1523 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0330 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl | 61 | 0.2680 | 1.3566 | 0.1356 | 1.1226 | 0.0292 |
| phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_seed0_trace/iter2_recovery_rate150/seed_000/trace.jsonl | 688 | 0.0562 | 1.4475 | 0.1420 | 0.2744 | 0.0402 |
| phase2_z0075_iter10_spike_local_recovery/seed_000/trace.jsonl | 80 | 0.2416 | 1.3367 | 0.1365 | 1.1367 | 0.0025 |
| phase2_z0075_iter10_spike_local_recovery/seed_001/trace.jsonl | 80 | 0.2220 | 1.3734 | 0.1295 | 1.1355 | 0.0124 |
| phase2_z0075_iter10_spike_local_recovery/seed_002/trace.jsonl | 80 | 0.2279 | 1.3251 | 0.1343 | 1.0973 | 0.0185 |
| phase2_z0075_iter10_spike_local_recovery/seed_003/trace.jsonl | 96 | 0.0242 | 1.4166 | 0.1350 | 0.1695 | 0.1558 |
| phase2_z0075_iter10_spike_local_recovery/seed_004/trace.jsonl | 80 | 0.2522 | 1.2913 | 0.1233 | 1.1600 | -0.0053 |
| phase2_z0075_iter10_spike_local_recovery/seed_006/trace.jsonl | 97 | 0.1981 | 1.3699 | 0.1218 | 1.0792 | -0.0021 |
| phase2_z0075_iter13_gain095_seed0_trace/iter13_gain095/seed_000/trace.jsonl | 750 | 0.0210 | 1.3576 | 0.1319 | 0.1781 | 0.1532 |
| phase2_z0075_iter2_seed7_pass_control_weighted/phase2_z0075_iter2_recovery_rate150_seed7_trace_control/iter2_recovery_rate150/seed_007/trace.jsonl | 750 | 0.0300 | 1.4407 | 0.1417 | 0.1976 | 0.1568 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_002/trace.jsonl | 156 | 0.1269 | 1.4552 | 0.1442 | 0.7764 | 0.0245 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl | 723 | 0.0518 | 1.4326 | 0.1404 | 0.2414 | 0.0246 |
| relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0265 | 1.4246 | 0.1371 | 0.1602 | 0.1527 |
| relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 501 | 0.0281 | 1.4498 | 0.1415 | 0.1189 | 0.1566 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0223 | 1.3621 | 0.1340 | 0.1819 | 0.1527 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_001/trace.jsonl | 560 | 0.0617 | 1.3677 | 0.1371 | 0.3217 | -0.0135 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_002/trace.jsonl | 643 | 0.0439 | 1.3111 | 0.1293 | 0.2792 | 0.0025 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_004/trace.jsonl | 478 | 0.0569 | 1.2914 | 0.1244 | 0.3303 | -0.0115 |
| rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0272 | 1.3721 | 0.1339 | 0.1496 | 0.1568 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
