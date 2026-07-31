# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `11fa288b6a53177c`
- entries: `3`
- samples: `2250`
- bc_ready_entries: `3`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0335 | 0.4189 | 1.7310 | 0.1543 | 0.1165 | 0.1556 |
| seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0374 | 0.4674 | 1.7409 | 0.1549 | 0.1177 | 0.1559 |
| seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0293 | 0.3661 | 1.7170 | 0.1538 | 0.1209 | 0.1554 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
