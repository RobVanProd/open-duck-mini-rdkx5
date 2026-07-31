# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `e6d3c1def23826e4`
- entries: `16`
- samples: `12000`
- bc_ready_entries: `16`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | 0.0093 | 0.0074 | 0.0349 | 0.0643 | 0.1613 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0009 | 0.0108 | 0.0071 | 0.0346 | 0.0678 | 0.1609 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0008 | 0.0102 | 0.0072 | 0.0342 | 0.0655 | 0.1614 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | 0.0083 | 0.0074 | 0.0344 | 0.0673 | 0.1612 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | 0.0082 | 0.0069 | 0.0345 | 0.0644 | 0.1615 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_005/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | 0.0084 | 0.0072 | 0.0350 | 0.0686 | 0.1610 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | 0.0089 | 0.0072 | 0.0367 | 0.0707 | 0.1611 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0009 | 0.0108 | 0.0065 | 0.0340 | 0.0663 | 0.1613 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0267 | 0.3338 | 1.4364 | 0.1405 | 0.1708 | 0.1590 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0280 | 0.3502 | 1.4362 | 0.1417 | 0.2022 | 0.1559 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0284 | 0.3556 | 1.4395 | 0.1404 | 0.1798 | 0.1584 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0246 | 0.3077 | 1.4402 | 0.1397 | 0.1780 | 0.1585 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0275 | 0.3436 | 1.4378 | 0.1408 | 0.2069 | 0.1583 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_005/trace.jsonl | 0-749 | 750 | `True` | 0.0303 | 0.3788 | 1.4333 | 0.1413 | 0.1810 | 0.1583 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0267 | 0.3333 | 1.4354 | 0.1415 | 0.1927 | 0.1563 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0289 | 0.3614 | 1.4355 | 0.1424 | 0.1753 | 0.1591 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
