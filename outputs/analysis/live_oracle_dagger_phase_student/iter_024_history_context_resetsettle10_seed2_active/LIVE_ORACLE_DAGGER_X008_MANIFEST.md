# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `72a3908eba69b224`
- entries: `5`
- samples: `3282`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0321 | 0.4012 | 1.4355 | 0.1400 | 0.1719 | 0.1587 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0284 | 0.3544 | 1.4368 | 0.1410 | 0.1913 | 0.1561 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-281 | 282 | `True` | -0.0441 | -0.5509 | 1.4153 | 0.1366 | 0.5337 | 0.0646 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0265 | 0.3311 | 1.4321 | 0.1392 | 0.1714 | 0.1577 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0278 | 0.3479 | 1.4292 | 0.1404 | 0.1777 | 0.1589 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
