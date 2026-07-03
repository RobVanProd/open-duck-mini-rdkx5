# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `ab8e509d5581e35a`
- entries: `8`
- samples: `6000`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_005/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0330 | 0.4130 | 1.5303 | 0.1443 | 0.1338 | 0.1522 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
