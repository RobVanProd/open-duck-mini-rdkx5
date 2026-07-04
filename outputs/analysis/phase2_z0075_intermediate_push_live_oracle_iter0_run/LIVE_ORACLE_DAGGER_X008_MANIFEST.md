# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `30f0b4dff11e8c38`
- entries: `2`
- samples: `1332`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0265 | 0.3313 | 1.4246 | 0.1371 | 0.1602 | 0.1527 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-581 | 582 | `True` | 0.0598 | 0.7473 | 1.4563 | 0.1419 | 0.2914 | -0.0052 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
