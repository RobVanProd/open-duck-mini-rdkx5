# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- `outputs/analysis/source_vx_selector_expansion_seeds8_15_trace_manifest.json`

## Thresholds

- min_entries: `8`
- min_samples: `100`
- min_mean_vx: `0.03`
- max_vy_abs_p95: `0.25`
- max_pitch_abs_p95: `0.25`
- min_base_height: `0.12`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.2`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `33`
- kept_entries: `19`
- rejected_entries: `14`
- samples: `9500`
- source_files: `19`
- max_source_fraction: `0.0526`

### Rejection Reasons

| reason | count |
|---|---:|
| `high_body_pitch` | 11 |
| `high_lateral_velocity` | 4 |
| `high_target_velocity` | 8 |
| `low_base_height` | 14 |
| `low_mean_vx` | 14 |
| `too_few_samples` | 8 |

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
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
