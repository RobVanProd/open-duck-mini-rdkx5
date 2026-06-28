# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `2f462e354caf1069`
- entries: `7`
- samples: `1750`
- bc_ready_entries: `7`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-249 | 250 | `True` | 0.0021 | 0.0257 | 0.2865 | 0.0429 | 0.0289 | 0.1519 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-249 | 250 | `True` | 0.0049 | 0.0610 | 0.8511 | 0.0728 | 0.0617 | 0.1563 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-249 | 250 | `True` | 0.0409 | 0.5114 | 1.7609 | 0.1527 | 0.1108 | 0.1511 |
| rollouts_x008/student/seed_003/trace.jsonl | 0-249 | 250 | `True` | 0.0315 | 0.3937 | 1.8475 | 0.1561 | 0.1271 | 0.1555 |
| rollouts_x008/student/seed_005/trace.jsonl | 0-249 | 250 | `True` | 0.0101 | 0.1257 | 0.5049 | 0.0530 | 0.1558 | 0.1464 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-249 | 250 | `True` | 0.0367 | 0.4594 | 1.8006 | 0.1543 | 0.1204 | 0.1530 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-249 | 250 | `True` | 0.0024 | 0.0297 | 0.7948 | 0.0668 | 0.0498 | 0.1564 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
