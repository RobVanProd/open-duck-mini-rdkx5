# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `e395c159e077d118`
- entries: `8`
- samples: `6000`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_full8_router_source_command_gated_traces/command_gated_zero0020/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0272 | 0.3403 | 1.4505 | 0.1402 | 0.1737 | 0.1581 |
| phase2_full8_router_source_command_gated_traces/command_gated_zero0020/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0254 | 0.3170 | 1.4478 | 0.1417 | 0.1876 | 0.1581 |
| phase2_full8_router_source_command_gated_traces/command_gated_zero0020/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0269 | 0.3367 | 1.4433 | 0.1409 | 0.1894 | 0.1581 |
| phase2_full8_router_source_command_gated_traces/command_gated_zero0020/seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0238 | 0.2975 | 1.4483 | 0.1407 | 0.1776 | 0.1581 |
| phase2_full8_router_source_command_gated_traces/command_gated_zero0020/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0244 | 0.3052 | 1.4456 | 0.1400 | 0.1830 | 0.1581 |
| phase2_full8_router_source_command_gated_traces/command_gated_zero0020/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0232 | 0.2896 | 1.4399 | 0.1405 | 0.1917 | 0.1581 |
| phase2_full8_router_source_command_gated_traces/command_gated_zero0020/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0265 | 0.3311 | 1.4524 | 0.1411 | 0.1724 | 0.1581 |
| phase2_full8_router_source_iter25_seed5_trace/iter25/seed_005/trace.jsonl | 0-749 | 750 | `True` | 0.0314 | 0.3924 | 1.4302 | 0.1415 | 0.1779 | 0.1589 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
