# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `c15e0ca8a2984d61`
- entries: `8`
- samples: `5336`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0240 | 0.2994 | 1.4255 | 0.1392 | 0.1795 | 0.1574 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0238 | 0.2978 | 1.4179 | 0.1409 | 0.1812 | 0.1574 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0225 | 0.2806 | 1.4243 | 0.1407 | 0.1885 | 0.1590 |
| rollouts_x008/student/seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0238 | 0.2969 | 1.4252 | 0.1397 | 0.1815 | 0.1582 |
| rollouts_x008/student/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0245 | 0.3065 | 1.4183 | 0.1397 | 0.1827 | 0.1584 |
| rollouts_x008/student/seed_005/trace.jsonl | 0-153 | 154 | `True` | 0.1363 | 1.7031 | 1.3947 | 0.1342 | 0.8275 | 0.0019 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-681 | 682 | `True` | 0.0466 | 0.5823 | 1.4183 | 0.1393 | 0.2482 | -0.0039 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0255 | 0.3182 | 1.4211 | 0.1407 | 0.1868 | 0.1590 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
