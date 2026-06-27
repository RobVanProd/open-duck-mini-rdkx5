# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `c9f8db0fac6d0022`
- entries: `19`
- samples: `10250`
- bc_ready_entries: `19`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0335 | 0.4189 | 1.7310 | 0.1543 | 0.1165 | 0.1556 |
| seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0374 | 0.4674 | 1.7409 | 0.1549 | 0.1177 | 0.1559 |
| seed_003/trace.jsonl | 0-749 | 750 | `True` | 0.0293 | 0.3661 | 1.7170 | 0.1538 | 0.1209 | 0.1554 |
| seed_000/trace.jsonl | 0-499 | 500 | `True` | 0.0004 | 0.0056 | 0.3100 | 0.0435 | 0.0250 | 0.1520 |
| seed_001/trace.jsonl | 0-499 | 500 | `True` | -0.0010 | -0.0126 | 0.3188 | 0.0442 | 0.0248 | 0.1556 |
| seed_002/trace.jsonl | 0-499 | 500 | `True` | 0.0016 | 0.0199 | 0.3049 | 0.0435 | 0.0211 | 0.1509 |
| seed_003/trace.jsonl | 0-499 | 500 | `True` | -0.0056 | -0.0697 | 0.2938 | 0.0428 | 0.0519 | 0.1549 |
| seed_004/trace.jsonl | 0-499 | 500 | `True` | 0.0031 | 0.0382 | 0.3054 | 0.0436 | 0.0351 | 0.1506 |
| seed_005/trace.jsonl | 0-499 | 500 | `True` | 0.0052 | 0.0653 | 0.3355 | 0.0453 | 0.1393 | 0.1463 |
| seed_006/trace.jsonl | 0-499 | 500 | `True` | -0.0016 | -0.0198 | 0.3245 | 0.0437 | 0.0213 | 0.1557 |
| seed_007/trace.jsonl | 0-499 | 500 | `True` | 0.0006 | 0.0072 | 0.3066 | 0.0431 | 0.0223 | 0.1559 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_000.jsonl | 0-499 | 500 | `True` | 0.0489 | 0.6109 | 2.3112 | 0.1834 | 0.0990 | 0.1520 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_001.jsonl | 0-499 | 500 | `True` | 0.0455 | 0.5690 | 2.3454 | 0.1850 | 0.0966 | 0.1556 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_002.jsonl | 0-499 | 500 | `True` | 0.0494 | 0.6172 | 2.2580 | 0.1809 | 0.0972 | 0.1509 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_003.jsonl | 0-499 | 500 | `True` | 0.0439 | 0.5491 | 2.2634 | 0.1824 | 0.1001 | 0.1554 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_004.jsonl | 0-499 | 500 | `True` | 0.0463 | 0.5784 | 2.3584 | 0.1836 | 0.0972 | 0.1506 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_005.jsonl | 0-499 | 500 | `True` | 0.0489 | 0.6115 | 2.3112 | 0.1835 | 0.1270 | 0.1462 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_006.jsonl | 0-499 | 500 | `True` | 0.0442 | 0.5527 | 2.3178 | 0.1863 | 0.0963 | 0.1557 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_007.jsonl | 0-499 | 500 | `True` | 0.0457 | 0.5719 | 2.3633 | 0.1847 | 0.0977 | 0.1557 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
