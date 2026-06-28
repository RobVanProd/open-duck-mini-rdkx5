# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `d93a51bd31c66031`
- entries: `2`
- samples: `500`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 0-249 | 250 | `True` | -0.0005 | NA | 0.0918 | 0.0286 | 0.0222 | 0.1520 |
| rollouts_x0/student/seed_004/trace.jsonl | 0-249 | 250 | `True` | 0.0032 | NA | 0.1099 | 0.0301 | 0.0350 | 0.1507 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
