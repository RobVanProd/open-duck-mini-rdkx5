# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `65eefb498dca9822`
- entries: `16`
- samples: `5166`
- bc_ready_entries: `16`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | 0-499 | 500 | `True` | 0.0489 | 0.6109 | 2.3112 | 0.1834 | 0.0990 | 0.1520 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | 0-499 | 500 | `True` | 0.0455 | 0.5690 | 2.3454 | 0.1850 | 0.0966 | 0.1556 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | 0-499 | 500 | `True` | 0.0494 | 0.6172 | 2.2580 | 0.1809 | 0.0972 | 0.1509 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | 0-499 | 500 | `True` | 0.0439 | 0.5491 | 2.2634 | 0.1824 | 0.1001 | 0.1554 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | 0-499 | 500 | `True` | 0.0463 | 0.5784 | 2.3584 | 0.1836 | 0.0972 | 0.1506 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | 0-499 | 500 | `True` | 0.0489 | 0.6115 | 2.3112 | 0.1835 | 0.1270 | 0.1462 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | 0-499 | 500 | `True` | 0.0442 | 0.5527 | 2.3178 | 0.1863 | 0.0963 | 0.1557 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | 0-499 | 500 | `True` | 0.0457 | 0.5719 | 2.3633 | 0.1847 | 0.0977 | 0.1557 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | 0-161 | 162 | `True` | -0.1024 | -1.2799 | 4.5303 | 0.1374 | 0.8119 | 0.0545 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | 0-291 | 292 | `True` | -0.0513 | -0.6412 | 4.3324 | 0.1347 | 0.4693 | 0.0676 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | 0-92 | 93 | `True` | -0.1642 | -2.0520 | 3.2618 | 0.1204 | 1.0255 | 0.0625 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | 0-230 | 231 | `True` | -0.0803 | -1.0032 | 4.1107 | 0.1394 | 0.5571 | 0.0763 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | 0-101 | 102 | `True` | -0.1499 | -1.8735 | 3.8893 | 0.1466 | 1.0228 | 0.0720 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl | 0-78 | 79 | `True` | -0.2006 | -2.5070 | 4.3573 | 0.1560 | 1.2144 | 0.0485 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | 0-116 | 117 | `True` | -0.1566 | -1.9572 | 4.2894 | 0.1179 | 0.9585 | 0.0580 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | 0-89 | 90 | `True` | -0.1875 | -2.3437 | 4.3555 | 0.1385 | 1.0918 | 0.0626 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
