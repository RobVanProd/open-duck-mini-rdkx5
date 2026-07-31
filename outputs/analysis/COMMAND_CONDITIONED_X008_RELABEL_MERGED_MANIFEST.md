# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_manifest.json`
- `outputs/analysis/command_conditioned_x008_relabel_manifest.json`

## Thresholds

- min_entries: `1`
- min_samples: `50`
- min_mean_vx: `-1.0`
- max_vy_abs_p95: `10.0`
- max_pitch_abs_p95: `1.0`
- min_base_height: `0.0`
- max_sent_velocity_p95: `10.0`
- max_tracking_p95: `10.0`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `22`
- kept_entries: `21`
- rejected_entries: `1`
- samples: `11250`
- source_files: `16`
- max_source_fraction: `0.0952`

### Rejection Reasons

| reason | count |
|---|---:|
| `high_body_pitch` | 1 |

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 500 | 0.0365 | 1.7470 | 0.1554 | 0.1188 | 0.1520 |
| seed_000/trace.jsonl | 500 | 0.0004 | 0.3100 | 0.0435 | 0.0250 | 0.1520 |
| seed_001/trace.jsonl | 750 | 0.0335 | 1.7310 | 0.1543 | 0.1165 | 0.1556 |
| seed_001/trace.jsonl | 500 | -0.0010 | 0.3188 | 0.0442 | 0.0248 | 0.1556 |
| seed_002/trace.jsonl | 500 | 0.0016 | 0.3049 | 0.0435 | 0.0211 | 0.1509 |
| seed_003/trace.jsonl | 500 | -0.0056 | 0.2938 | 0.0428 | 0.0519 | 0.1549 |
| seed_003/trace.jsonl | 750 | 0.0293 | 1.7170 | 0.1538 | 0.1209 | 0.1554 |
| seed_004/trace.jsonl | 500 | 0.0031 | 0.3054 | 0.0436 | 0.0351 | 0.1506 |
| seed_005/trace.jsonl | 500 | 0.0052 | 0.3355 | 0.0453 | 0.1393 | 0.1463 |
| seed_005/trace.jsonl | 500 | 0.0362 | 1.7179 | 0.1530 | 0.1492 | 0.1462 |
| seed_006/trace.jsonl | 500 | -0.0016 | 0.3245 | 0.0437 | 0.0213 | 0.1557 |
| seed_007/trace.jsonl | 500 | 0.0006 | 0.3066 | 0.0431 | 0.0223 | 0.1559 |
| seed_007/trace.jsonl | 750 | 0.0374 | 1.7409 | 0.1549 | 0.1177 | 0.1559 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_000.jsonl | 500 | 0.0489 | 2.3112 | 0.1834 | 0.0990 | 0.1520 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_001.jsonl | 500 | 0.0455 | 2.3454 | 0.1850 | 0.0966 | 0.1556 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_002.jsonl | 500 | 0.0494 | 2.2580 | 0.1809 | 0.0972 | 0.1509 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_003.jsonl | 500 | 0.0439 | 2.2634 | 0.1824 | 0.1001 | 0.1554 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_004.jsonl | 500 | 0.0463 | 2.3584 | 0.1836 | 0.0972 | 0.1506 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_005.jsonl | 500 | 0.0489 | 2.3112 | 0.1835 | 0.1270 | 0.1462 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_006.jsonl | 500 | 0.0442 | 2.3178 | 0.1863 | 0.0963 | 0.1557 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_007.jsonl | 500 | 0.0457 | 2.3633 | 0.1847 | 0.0977 | 0.1557 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
