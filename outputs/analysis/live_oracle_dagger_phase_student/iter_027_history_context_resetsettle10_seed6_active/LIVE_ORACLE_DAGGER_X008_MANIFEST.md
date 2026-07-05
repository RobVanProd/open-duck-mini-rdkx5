# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `2898911323e2860d`
- entries: `5`
- samples: `3250`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0261 | 0.3256 | 1.4374 | 0.1398 | 0.1922 | 0.1591 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0287 | 0.3584 | 1.4287 | 0.1404 | 0.1786 | 0.1585 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0262 | 0.3278 | 1.4432 | 0.1397 | 0.1822 | 0.1590 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-249 | 250 | `True` | -0.0453 | -0.5659 | 1.4001 | 0.1366 | 0.5799 | 0.0690 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0275 | 0.3437 | 1.4299 | 0.1405 | 0.1863 | 0.1565 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
