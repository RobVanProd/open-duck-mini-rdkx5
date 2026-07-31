# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/filtered_source_vx_selector_dagger6_recovery_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`
- `outputs/analysis/dagger6_targeted_recovery_teacher_relabel_manifest.json`

## Thresholds

- min_entries: `1`
- min_samples: `1`
- min_mean_vx: `-1.0`
- max_vy_abs_p95: `10.0`
- max_pitch_abs_p95: `10.0`
- min_base_height: `0.0`
- max_sent_velocity_p95: `10.0`
- max_tracking_p95: `10.0`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `143`
- kept_entries: `143`
- rejected_entries: `0`
- samples: `22778`
- source_files: `35`
- max_source_fraction: `0.3636`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 500 | 0.0225 | 2.1727 | 0.1705 | 0.0536 | 0.1536 |
| seed_000/trace.jsonl | 500 | 0.0225 | 2.1727 | 0.1705 | 0.0536 | 0.1536 |
| seed_001/trace.jsonl | 32 | 0.0026 | 1.9167 | 0.1222 | 0.1575 | 0.1050 |
| seed_001/trace.jsonl | 32 | 0.0026 | 1.9167 | 0.1222 | 0.1575 | 0.1050 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_001/trace.jsonl | 31 | 0.0109 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_002/trace.jsonl | 500 | 0.0255 | 2.2042 | 0.1756 | 0.0503 | 0.1525 |
| seed_002/trace.jsonl | 500 | 0.0255 | 2.2042 | 0.1756 | 0.0503 | 0.1525 |
| seed_003/trace.jsonl | 500 | 0.0203 | 2.1781 | 0.1750 | 0.0661 | 0.1579 |
| seed_003/trace.jsonl | 500 | 0.0203 | 2.1781 | 0.1750 | 0.0661 | 0.1579 |
| seed_004/trace.jsonl | 500 | 0.0225 | 2.1495 | 0.1722 | 0.0631 | 0.1515 |
| seed_004/trace.jsonl | 500 | 0.0225 | 2.1495 | 0.1722 | 0.0631 | 0.1515 |
| seed_005/trace.jsonl | 500 | 0.0279 | 2.1776 | 0.1770 | 0.1506 | 0.1468 |
| seed_005/trace.jsonl | 500 | 0.0279 | 2.1776 | 0.1770 | 0.1506 | 0.1468 |
| seed_006/trace.jsonl | 500 | 0.0199 | 2.1656 | 0.1762 | 0.0632 | 0.1582 |
| seed_006/trace.jsonl | 500 | 0.0199 | 2.1656 | 0.1762 | 0.0632 | 0.1582 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0268 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |
| seed_007/trace.jsonl | 32 | 0.0292 | 1.8301 | 0.1536 | 0.0216 | 0.0996 |
| seed_007/trace.jsonl | 32 | 0.0292 | 1.8301 | 0.1536 | 0.0216 | 0.0996 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_016.jsonl | 500 | 0.0320 | 2.3134 | 0.1809 | 0.0753 | 0.1594 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_017.jsonl | 500 | 0.0316 | 2.2873 | 0.1793 | 0.0623 | 0.1549 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_018.jsonl | 500 | 0.0375 | 2.2734 | 0.1815 | 0.0581 | 0.1534 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_022.jsonl | 500 | 0.0322 | 2.3067 | 0.1818 | 0.0575 | 0.1549 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_024.jsonl | 500 | 0.0378 | 2.3020 | 0.1791 | 0.0546 | 0.1542 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_027.jsonl | 500 | 0.0315 | 2.2873 | 0.1815 | 0.0638 | 0.1579 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_029.jsonl | 500 | 0.0315 | 2.2918 | 0.1806 | 0.0592 | 0.1559 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_031.jsonl | 500 | 0.0324 | 2.2983 | 0.1793 | 0.0614 | 0.1556 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_008.jsonl | 500 | 0.0315 | 2.2935 | 0.1820 | 0.0594 | 0.1487 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_010.jsonl | 500 | 0.0336 | 2.2931 | 0.1830 | 0.0607 | 0.1514 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_011.jsonl | 500 | 0.0322 | 2.2689 | 0.1821 | 0.0709 | 0.1587 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | 500 | 0.0489 | 2.3112 | 0.1834 | 0.0990 | 0.1520 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | 500 | 0.0455 | 2.3454 | 0.1850 | 0.0966 | 0.1556 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | 500 | 0.0494 | 2.2580 | 0.1809 | 0.0972 | 0.1509 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | 500 | 0.0439 | 2.2634 | 0.1824 | 0.1001 | 0.1554 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | 500 | 0.0463 | 2.3584 | 0.1836 | 0.0972 | 0.1506 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | 500 | 0.0489 | 2.3112 | 0.1835 | 0.1270 | 0.1462 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | 500 | 0.0442 | 2.3178 | 0.1863 | 0.0963 | 0.1557 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | 500 | 0.0457 | 2.3633 | 0.1847 | 0.0977 | 0.1557 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | 500 | 0.0503 | 2.1249 | 0.1823 | 0.0933 | 0.1520 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | 500 | 0.0463 | 2.1036 | 0.1824 | 0.0953 | 0.1556 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | 500 | 0.0521 | 2.1235 | 0.1840 | 0.0985 | 0.1509 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | 500 | 0.0459 | 2.0693 | 0.1801 | 0.0997 | 0.1557 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | 500 | 0.0487 | 2.1221 | 0.1838 | 0.1015 | 0.1506 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | 500 | 0.0445 | 2.0851 | 0.1833 | 0.0992 | 0.1557 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | 500 | 0.0477 | 2.1263 | 0.1808 | 0.0963 | 0.1559 |
| source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl | 500 | 0.0360 | 2.1754 | 0.1767 | 0.1020 | 0.1559 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
