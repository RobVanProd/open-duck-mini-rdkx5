# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `24beb17ef0e1de02`
- entries: `10`
- samples: `7500`
- bc_ready_entries: `10`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0008 | 0.0094 | 0.0000 | 0.0349 | 0.0633 | 0.1614 |
| seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0009 | 0.0107 | 0.0000 | 0.0346 | 0.0667 | 0.1609 |
| seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0008 | 0.0100 | 0.0000 | 0.0346 | 0.0647 | 0.1614 |
| seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | 0.0089 | 0.0000 | 0.0367 | 0.0699 | 0.1611 |
| seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0009 | 0.0106 | 0.0000 | 0.0341 | 0.0657 | 0.1613 |
| seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0272 | 0.3403 | 1.4505 | 0.1402 | 0.1737 | 0.1581 |
| seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0254 | 0.3170 | 1.4478 | 0.1417 | 0.1876 | 0.1581 |
| seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0269 | 0.3367 | 1.4433 | 0.1409 | 0.1894 | 0.1581 |
| seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0232 | 0.2896 | 1.4399 | 0.1405 | 0.1917 | 0.1581 |
| seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0265 | 0.3311 | 1.4524 | 0.1411 | 0.1724 | 0.1581 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
