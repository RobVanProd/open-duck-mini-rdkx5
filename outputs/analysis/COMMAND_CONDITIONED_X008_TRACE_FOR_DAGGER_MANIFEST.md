# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `604b95a3e4b4bef2`
- entries: `2`
- samples: `1000`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 0-499 | 500 | `True` | 0.0365 | 0.4560 | 1.7470 | 0.1554 | 0.1188 | 0.1520 |
| seed_005/trace.jsonl | 0-499 | 500 | `True` | 0.0362 | 0.4527 | 1.7179 | 0.1530 | 0.1492 | 0.1462 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
