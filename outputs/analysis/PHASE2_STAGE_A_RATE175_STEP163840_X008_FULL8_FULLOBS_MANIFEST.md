# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `f0c6f2d5e74f8bff`
- entries: `8`
- samples: `400`
- bc_ready_entries: `8`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 0-49 | 50 | `True` | 0.0346 | 0.4326 | 1.3507 | 0.1330 | 0.0998 | 0.1520 |
| seed_001/trace.jsonl | 0-49 | 50 | `True` | 0.0257 | 0.3214 | 1.3835 | 0.1284 | 0.1095 | 0.1556 |
| seed_002/trace.jsonl | 0-49 | 50 | `True` | 0.0517 | 0.6466 | 1.4203 | 0.1369 | 0.0988 | 0.1509 |
| seed_003/trace.jsonl | 0-49 | 50 | `True` | -0.0455 | -0.5686 | 1.3565 | 0.1306 | 0.2270 | 0.1555 |
| seed_004/trace.jsonl | 0-49 | 50 | `True` | 0.0544 | 0.6795 | 1.2776 | 0.1303 | 0.0951 | 0.1506 |
| seed_005/trace.jsonl | 0-49 | 50 | `True` | 0.0583 | 0.7285 | 1.3592 | 0.1359 | 0.2134 | 0.1462 |
| seed_006/trace.jsonl | 0-49 | 50 | `True` | 0.0114 | 0.1422 | 1.3596 | 0.1348 | 0.0882 | 0.1557 |
| seed_007/trace.jsonl | 0-49 | 50 | `True` | 0.0358 | 0.4474 | 1.3396 | 0.1316 | 0.1012 | 0.1559 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
