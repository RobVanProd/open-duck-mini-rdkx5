# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `1f3fdb534fdad687`
- entries: `2`
- samples: `812`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 0-61 | 62 | `True` | -0.2639 | NA | 4.6431 | 0.1115 | 1.1872 | 0.0721 |
| rollouts_x0/student/seed_001/trace.jsonl | 0-749 | 750 | `True` | -0.0002 | NA | 0.0803 | 0.0368 | 0.0672 | 0.1568 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
