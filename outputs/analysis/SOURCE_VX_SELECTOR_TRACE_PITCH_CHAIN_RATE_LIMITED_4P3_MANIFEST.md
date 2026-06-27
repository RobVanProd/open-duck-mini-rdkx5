# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `3aedbacc4a592fc8`
- entries: `8`
- samples: `4000`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_000.jsonl | 0-499 | 500 | `True` | 0.0489 | 0.6109 | 2.3112 | 0.1834 | 0.0990 | 0.1520 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_001.jsonl | 0-499 | 500 | `True` | 0.0455 | 0.5690 | 2.3454 | 0.1850 | 0.0966 | 0.1556 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_002.jsonl | 0-499 | 500 | `True` | 0.0494 | 0.6172 | 2.2580 | 0.1809 | 0.0972 | 0.1509 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_003.jsonl | 0-499 | 500 | `True` | 0.0439 | 0.5491 | 2.2634 | 0.1824 | 0.1001 | 0.1554 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_004.jsonl | 0-499 | 500 | `True` | 0.0463 | 0.5784 | 2.3584 | 0.1836 | 0.0972 | 0.1506 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_005.jsonl | 0-499 | 500 | `True` | 0.0489 | 0.6115 | 2.3112 | 0.1835 | 0.1270 | 0.1462 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_006.jsonl | 0-499 | 500 | `True` | 0.0442 | 0.5527 | 2.3178 | 0.1863 | 0.0963 | 0.1557 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_007.jsonl | 0-499 | 500 | `True` | 0.0457 | 0.5719 | 2.3633 | 0.1847 | 0.0977 | 0.1557 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
