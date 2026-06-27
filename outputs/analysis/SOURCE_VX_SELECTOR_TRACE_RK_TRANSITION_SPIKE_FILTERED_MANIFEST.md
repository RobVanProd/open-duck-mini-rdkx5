# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `69c1466221e946cc`
- entries: `8`
- samples: `3124`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_000.jsonl | 0-499 | 392 | `True` | 0.0459 | 0.5739 | 3.0842 | 0.1826 | 0.0987 | 0.1520 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_001.jsonl | 0-499 | 387 | `True` | 0.0416 | 0.5201 | 3.1161 | 0.1837 | 0.0977 | 0.1556 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_002.jsonl | 0-499 | 395 | `True` | 0.0474 | 0.5923 | 3.0387 | 0.1793 | 0.0974 | 0.1509 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_003.jsonl | 0-499 | 388 | `True` | 0.0414 | 0.5171 | 3.1511 | 0.1820 | 0.1000 | 0.1554 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_004.jsonl | 0-499 | 393 | `True` | 0.0427 | 0.5344 | 3.0722 | 0.1837 | 0.0975 | 0.1506 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_005.jsonl | 0-499 | 386 | `True` | 0.0468 | 0.5851 | 3.1516 | 0.1823 | 0.1289 | 0.1462 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_006.jsonl | 0-499 | 386 | `True` | 0.0416 | 0.5200 | 3.1576 | 0.1850 | 0.0960 | 0.1557 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_007.jsonl | 0-499 | 397 | `True` | 0.0427 | 0.5341 | 3.0241 | 0.1834 | 0.0981 | 0.1557 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
