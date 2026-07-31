# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_merged_manifest.json`
- `outputs/analysis/phase2_z0075_iter21_seed5_late_push_recovery_relabel_manifest.json`

## Thresholds

- min_entries: `1`
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

- input_entries: `89`
- kept_entries: `89`
- rejected_entries: `0`
- samples: `53209`
- source_files: `78`
- max_source_fraction: `0.0337`

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
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl | 61 | 0.2680 | 1.3566 | 0.1356 | 1.1226 | 0.0292 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_002/push_009_e969257189933035.jsonl | 42 | -0.3378 | 1.4119 | 0.1278 | 1.1762 | 0.1021 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl | 64 | -0.2441 | 1.4153 | 0.1350 | 1.0869 | 0.0961 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_011_420a187c0ff36573.jsonl | 8 | -1.0104 | 1.2869 | 0.1253 | 1.3573 | 0.0961 |
| phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_seed0_trace/iter2_recovery_rate150/seed_000/trace.jsonl | 688 | 0.0562 | 1.4475 | 0.1420 | 0.2744 | 0.0402 |
| phase2_z0075_iter10_spike_local_recovery/seed_000/trace.jsonl | 80 | 0.2416 | 1.3367 | 0.1365 | 1.1367 | 0.0025 |
| phase2_z0075_iter10_spike_local_recovery/seed_001/trace.jsonl | 80 | 0.2220 | 1.3734 | 0.1295 | 1.1355 | 0.0124 |
| phase2_z0075_iter10_spike_local_recovery/seed_002/trace.jsonl | 80 | 0.2279 | 1.3251 | 0.1343 | 1.0973 | 0.0185 |
| phase2_z0075_iter10_spike_local_recovery/seed_003/trace.jsonl | 96 | 0.0242 | 1.4166 | 0.1350 | 0.1695 | 0.1558 |
| phase2_z0075_iter10_spike_local_recovery/seed_004/trace.jsonl | 80 | 0.2522 | 1.2913 | 0.1233 | 1.1600 | -0.0053 |
| phase2_z0075_iter10_spike_local_recovery/seed_005/trace.jsonl | 46 | -0.3199 | 1.4587 | 0.1397 | 1.3732 | 0.0695 |
| phase2_z0075_iter10_spike_local_recovery/seed_006/trace.jsonl | 97 | 0.1981 | 1.3699 | 0.1218 | 1.0792 | -0.0021 |
| phase2_z0075_iter21_early_lunge_gain095_relabel/seed_000/trace.jsonl | 31 | 0.1385 | 1.5344 | 0.1316 | 0.5418 | 0.1476 |
| phase2_z0075_iter21_seed5_late_push_recovery_snippets_relabelled/analysis/phase2_z0075_iter21_seed5_late_push_recovery_snippets/seed_005/push_009_200a8ce383346549.jsonl | 79 | -0.2016 | 1.3650 | 0.1245 | 1.0836 | 0.0873 |
| phase2_z0075_iter2_seed7_pass_control_weighted/phase2_z0075_iter2_recovery_rate150_seed7_trace_control/iter2_recovery_rate150/seed_007/trace.jsonl | 750 | 0.0300 | 1.4407 | 0.1417 | 0.1976 | 0.1568 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_001/trace.jsonl | 493 | -0.0058 | 1.4270 | 0.1406 | 0.2827 | 0.1047 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_002/trace.jsonl | 156 | 0.1269 | 1.4552 | 0.1442 | 0.7764 | 0.0245 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_003/trace.jsonl | 449 | -0.0186 | 1.4263 | 0.1377 | 0.2721 | 0.0996 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl | 723 | 0.0518 | 1.4326 | 0.1404 | 0.2414 | 0.0246 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_005/trace.jsonl | 46 | -0.2873 | 1.4343 | 0.1333 | 1.2367 | 0.0928 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_006/trace.jsonl | 245 | -0.0458 | 1.3961 | 0.1334 | 0.5608 | 0.0923 |
| relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | 750 | -0.0002 | 0.0803 | 0.0368 | 0.0672 | 0.1568 |
| relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0265 | 1.4246 | 0.1371 | 0.1602 | 0.1527 |
| relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | 501 | 0.0281 | 1.4498 | 0.1415 | 0.1189 | 0.1566 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | -0.0005 | 0.0393 | 0.0280 | 0.0320 | 0.1529 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | -0.0004 | 0.0584 | 0.0286 | 0.0344 | 0.1528 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | -0.0005 | 0.0952 | 0.0361 | 0.0662 | 0.1568 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | -0.0005 | 0.0471 | 0.0358 | 0.0624 | 0.1568 |
| rollouts_x0/student/seed_002/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_003/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_004/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_005/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_006/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x0/student/seed_007/trace.jsonl | 750 | 0.0001 | 0.0300 | 0.0310 | 0.0168 | 0.1524 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0223 | 1.3621 | 0.1340 | 0.1819 | 0.1527 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_001/trace.jsonl | 560 | 0.0617 | 1.3677 | 0.1371 | 0.3217 | -0.0135 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_002/trace.jsonl | 643 | 0.0439 | 1.3111 | 0.1293 | 0.2792 | 0.0025 |
| rollouts_x008/student/seed_003/trace.jsonl | 85 | -0.2159 | 1.7019 | 0.1038 | 1.1493 | 0.0708 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_004/trace.jsonl | 478 | 0.0569 | 1.2914 | 0.1244 | 0.3303 | -0.0115 |
| rollouts_x008/student/seed_005/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_005/trace.jsonl | 48 | -0.2883 | 2.8510 | 0.1216 | 1.2752 | 0.0875 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0262 | 1.4875 | 0.1442 | 0.1320 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0272 | 1.3721 | 0.1339 | 0.1496 | 0.1568 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
