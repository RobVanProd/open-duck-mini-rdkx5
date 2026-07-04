# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `e518de15e8f9e0cb`
- entries: `5`
- samples: `1814`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_001/trace.jsonl | 0-559 | 560 | `True` | 0.0617 | 0.7718 | 1.3677 | 0.1371 | 0.3217 | -0.0135 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-642 | 643 | `True` | 0.0439 | 0.5482 | 1.3111 | 0.1293 | 0.2792 | 0.0025 |
| rollouts_x008/student/seed_003/trace.jsonl | 0-84 | 85 | `True` | -0.2159 | -2.6989 | 1.7019 | 0.1038 | 1.1493 | 0.0708 |
| rollouts_x008/student/seed_004/trace.jsonl | 0-477 | 478 | `True` | 0.0569 | 0.7113 | 1.2914 | 0.1244 | 0.3303 | -0.0115 |
| rollouts_x008/student/seed_005/trace.jsonl | 0-47 | 48 | `True` | -0.2883 | -3.6031 | 2.8510 | 0.1216 | 1.2752 | 0.0875 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
