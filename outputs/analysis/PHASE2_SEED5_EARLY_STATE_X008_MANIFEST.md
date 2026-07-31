# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `e2fd723027cad7b6`
- entries: `1`
- samples: `25`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_005/trace.jsonl | 0-24 | 25 | `True` | 0.0201 | 0.2516 | 1.8359 | 0.1652 | 0.2202 | 0.1465 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
