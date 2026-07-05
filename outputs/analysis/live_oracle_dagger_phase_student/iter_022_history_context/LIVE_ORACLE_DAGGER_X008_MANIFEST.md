# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `bbaff0a289bbda53`
- entries: `5`
- samples: `2594`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 0-114 | 115 | `True` | 0.1803 | 2.2538 | 1.3654 | 0.1301 | 0.9956 | -0.0053 |
| rollouts_x008/student/seed_001/trace.jsonl | 0-228 | 229 | `True` | 0.0984 | 1.2296 | 1.3941 | 0.1366 | 0.6725 | 0.0195 |
| rollouts_x008/student/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0301 | 0.3763 | 1.4303 | 0.1391 | 0.1673 | 0.1532 |
| rollouts_x008/student/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0281 | 0.3514 | 1.4391 | 0.1399 | 0.1641 | 0.1532 |
| rollouts_x008/student/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0289 | 0.3616 | 1.4281 | 0.1389 | 0.1830 | 0.1532 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
