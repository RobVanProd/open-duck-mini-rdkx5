# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `638b77d55bbe2c1e`
- entries: `2`
- samples: `63`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_001/trace.jsonl | 0-30 | 31 | `True` | 0.0109 | 0.1366 | 2.1562 | 0.1769 | 0.1818 | 0.0974 |
| seed_007/trace.jsonl | 0-31 | 32 | `True` | 0.0268 | 0.3345 | 2.0335 | 0.1690 | 0.0446 | 0.0949 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
