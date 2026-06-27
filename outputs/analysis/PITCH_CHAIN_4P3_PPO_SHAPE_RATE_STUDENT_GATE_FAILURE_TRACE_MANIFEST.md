# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `e6ec0847403abc68`
- entries: `2`
- samples: `1000`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_001/trace.jsonl | 0-499 | 500 | `True` | 0.0359 | 0.4484 | 2.2263 | 0.1765 | 0.0991 | 0.1556 |
| seed_004/trace.jsonl | 0-499 | 500 | `True` | 0.0393 | 0.4918 | 2.1565 | 0.1723 | 0.0967 | 0.1506 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
