# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `43bdc25b8b38d29e`
- entries: `2`
- samples: `860`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-109 | 110 | `True` | 0.1799 | 2.2491 | 1.4147 | 0.1376 | 1.0237 | 0.0140 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0331 | 0.4139 | 1.4459 | 0.1388 | 0.1668 | 0.1532 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
