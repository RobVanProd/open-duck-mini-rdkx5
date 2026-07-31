# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `ee1d17522a754da8`
- entries: `8`
- samples: `3064`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 0-499 | 500 | `True` | 0.0225 | 0.2808 | 2.1727 | 0.1705 | 0.0536 | 0.1536 |
| seed_001/trace.jsonl | 0-31 | 32 | `True` | 0.0026 | 0.0323 | 1.9167 | 0.1222 | 0.1575 | 0.1050 |
| seed_002/trace.jsonl | 0-499 | 500 | `True` | 0.0255 | 0.3189 | 2.2042 | 0.1756 | 0.0503 | 0.1525 |
| seed_003/trace.jsonl | 0-499 | 500 | `True` | 0.0203 | 0.2536 | 2.1781 | 0.1750 | 0.0661 | 0.1579 |
| seed_004/trace.jsonl | 0-499 | 500 | `True` | 0.0225 | 0.2807 | 2.1495 | 0.1722 | 0.0631 | 0.1515 |
| seed_005/trace.jsonl | 0-499 | 500 | `True` | 0.0279 | 0.3492 | 2.1776 | 0.1770 | 0.1506 | 0.1468 |
| seed_006/trace.jsonl | 0-499 | 500 | `True` | 0.0199 | 0.2491 | 2.1656 | 0.1762 | 0.0632 | 0.1582 |
| seed_007/trace.jsonl | 0-31 | 32 | `True` | 0.0292 | 0.3649 | 1.8301 | 0.1536 | 0.0216 | 0.0996 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
