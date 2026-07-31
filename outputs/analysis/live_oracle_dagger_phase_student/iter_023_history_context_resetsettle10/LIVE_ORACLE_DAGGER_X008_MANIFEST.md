# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `61c4d17e24984b61`
- entries: `5`
- samples: `3009`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-638 | 639 | `True` | 0.0016 | 0.0197 | 1.4646 | 0.1426 | 0.2264 | 0.0706 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0318 | 0.3979 | 1.4593 | 0.1441 | 0.2211 | 0.1580 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0327 | 0.4087 | 1.4600 | 0.1425 | 0.1792 | 0.1585 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-119 | 120 | `True` | 0.1618 | 2.0231 | 1.3716 | 0.1320 | 0.9614 | 0.0116 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0298 | 0.3726 | 1.4692 | 0.1425 | 0.1652 | 0.1589 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
