# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `3488cc74affefdad`
- entries: `2`
- samples: `1500`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | -0.0005 | NA | 0.0393 | 0.0280 | 0.0320 | 0.1529 |
| rollouts_x0/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | -0.0005 | NA | 0.0471 | 0.0358 | 0.0624 | 0.1568 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
