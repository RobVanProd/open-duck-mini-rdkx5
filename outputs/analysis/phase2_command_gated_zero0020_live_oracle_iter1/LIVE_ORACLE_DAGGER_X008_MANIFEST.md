# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `f59e311d6dcaf357`
- entries: `2`
- samples: `1413`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-662 | 663 | `True` | -0.0018 | -0.0230 | 1.4326 | 0.1386 | 0.2192 | 0.0636 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | -0.0011 | -0.0140 | 1.4281 | 0.1370 | 0.2037 | 0.0737 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
