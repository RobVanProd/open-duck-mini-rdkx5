# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `f913130b73894fea`
- entries: `2`
- samples: `1500`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | NA | 0.3442 | 0.0453 | 0.0345 | 0.1523 |
| rollouts_x0/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | NA | 0.3442 | 0.0453 | 0.0345 | 0.1523 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
