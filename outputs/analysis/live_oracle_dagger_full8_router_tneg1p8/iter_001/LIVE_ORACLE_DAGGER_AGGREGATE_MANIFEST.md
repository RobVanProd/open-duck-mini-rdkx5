# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest_seed56_weighted.json`
- `outputs/analysis/live_oracle_dagger_full8_router_tneg1p8/iter_001/live_oracle_dagger_x008_manifest.json`
- `outputs/analysis/live_oracle_dagger_full8_router_tneg1p8/iter_001/live_oracle_dagger_x0_manifest.json`

## Thresholds

- min_entries: `11`
- min_samples: `1`
- min_mean_vx: `-10.0`
- max_vy_abs_p95: `999.0`
- max_pitch_abs_p95: `999.0`
- min_base_height: `-10.0`
- max_sent_velocity_p95: `999.0`
- max_tracking_p95: `999.0`
- include_source_regex: `None`
- exclude_source_regex: `None`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `26`
- kept_entries: `26`
- rejected_entries: `0`
- samples: `18836`
- source_files: `26`
- max_source_fraction: `0.0385`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_000/trace.jsonl | 750 | 0.0007 | 0.0074 | 0.0349 | 0.0643 | 0.1613 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_001/trace.jsonl | 750 | 0.0009 | 0.0071 | 0.0346 | 0.0678 | 0.1609 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_002/trace.jsonl | 750 | 0.0008 | 0.0072 | 0.0342 | 0.0655 | 0.1614 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_003/trace.jsonl | 750 | 0.0007 | 0.0074 | 0.0344 | 0.0673 | 0.1612 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_004/trace.jsonl | 750 | 0.0007 | 0.0069 | 0.0345 | 0.0644 | 0.1615 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_005/trace.jsonl | 750 | 0.0007 | 0.0072 | 0.0350 | 0.0686 | 0.1610 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_006/trace.jsonl | 750 | 0.0007 | 0.0072 | 0.0367 | 0.0707 | 0.1611 |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_007/trace.jsonl | 750 | 0.0009 | 0.0065 | 0.0340 | 0.0663 | 0.1613 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_000/trace.jsonl | 750 | 0.0267 | 1.4364 | 0.1405 | 0.1708 | 0.1590 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_001/trace.jsonl | 750 | 0.0280 | 1.4362 | 0.1417 | 0.2022 | 0.1559 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_002/trace.jsonl | 750 | 0.0284 | 1.4395 | 0.1404 | 0.1798 | 0.1584 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_003/trace.jsonl | 750 | 0.0246 | 1.4402 | 0.1397 | 0.1780 | 0.1585 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_004/trace.jsonl | 750 | 0.0275 | 1.4378 | 0.1408 | 0.2069 | 0.1583 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_005/trace.jsonl | 750 | 0.0303 | 1.4333 | 0.1413 | 0.1810 | 0.1583 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_006/trace.jsonl | 750 | 0.0267 | 1.4354 | 0.1415 | 0.1927 | 0.1563 |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_007/trace.jsonl | 750 | 0.0289 | 1.4355 | 0.1424 | 0.1753 | 0.1591 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0007 | 0.0132 | 0.0351 | 0.0641 | 0.1613 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0009 | 0.0132 | 0.0347 | 0.0670 | 0.1609 |
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0.0240 | 1.4255 | 0.1392 | 0.1795 | 0.1574 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0.0238 | 1.4179 | 0.1409 | 0.1812 | 0.1574 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0.0225 | 1.4243 | 0.1407 | 0.1885 | 0.1590 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0.0238 | 1.4252 | 0.1397 | 0.1815 | 0.1582 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0.0245 | 1.4183 | 0.1397 | 0.1827 | 0.1584 |
| rollouts_x008/student/seed_005/trace.jsonl | 154 | 0.1363 | 1.3947 | 0.1342 | 0.8275 | 0.0019 |
| rollouts_x008/student/seed_006/trace.jsonl | 682 | 0.0466 | 1.4183 | 0.1393 | 0.2482 | -0.0039 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0.0255 | 1.4211 | 0.1407 | 0.1868 | 0.1590 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
