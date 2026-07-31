# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `04447d35724a6b50`
- entries: `8`
- samples: `6000`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0289 | 0.3616 | 1.7335 | 0.1547 | 0.1180 | 0.1519 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0322 | 0.4028 | 1.7518 | 0.1562 | 0.1213 | 0.1563 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0316 | 0.3949 | 1.7549 | 0.1560 | 0.1151 | 0.1512 |
| rollouts_x008/student/seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0255 | 0.3184 | 1.7394 | 0.1535 | 0.1177 | 0.1547 |
| rollouts_x008/student/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0318 | 0.3971 | 1.7427 | 0.1545 | 0.1120 | 0.1506 |
| rollouts_x008/student/seed_005/trace.jsonl | 0-749 | 750 | `True` | 0.0298 | 0.3721 | 1.7480 | 0.1543 | 0.1470 | 0.1464 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0312 | 0.3903 | 1.7429 | 0.1559 | 0.1130 | 0.1531 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0285 | 0.3562 | 1.7374 | 0.1531 | 0.1082 | 0.1564 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
