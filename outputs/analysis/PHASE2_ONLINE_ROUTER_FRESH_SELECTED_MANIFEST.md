# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `f2ecbdfab21ccafa`
- entries: `5`
- samples: `3750`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_online_router_fresh_iter24_25/iter24/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0261 | 0.3256 | 1.4374 | 0.1398 | 0.1922 | 0.1591 |
| phase2_online_router_fresh_iter24_25/iter24/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0262 | 0.3278 | 1.4432 | 0.1397 | 0.1822 | 0.1590 |
| phase2_online_router_fresh_iter24_25/iter24/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0275 | 0.3437 | 1.4299 | 0.1405 | 0.1863 | 0.1565 |
| phase2_online_router_fresh_iter24_25/iter25/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0285 | 0.3567 | 1.4341 | 0.1413 | 0.1739 | 0.1579 |
| phase2_online_router_fresh_iter24_25/iter25/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0262 | 0.3273 | 1.4214 | 0.1407 | 0.1904 | 0.1580 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
