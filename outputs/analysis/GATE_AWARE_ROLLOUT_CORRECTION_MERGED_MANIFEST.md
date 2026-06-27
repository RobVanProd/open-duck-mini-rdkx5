# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- `outputs/analysis/gate_aware_rollout_correction_manifest.json`

## Thresholds

- min_entries: `10`
- min_samples: `100`
- min_mean_vx: `-1.0`
- max_vy_abs_p95: `999.0`
- max_pitch_abs_p95: `999.0`
- min_base_height: `0.0`
- max_sent_velocity_p95: `999.0`
- max_tracking_p95: `999.0`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `10`
- kept_entries: `10`
- rejected_entries: `0`
- samples: `5000`
- source_files: `10`
- max_source_fraction: `0.1000`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| ppo_warmstart_restore_policy_kl100_640/seed_001/trace.jsonl | 500 | -0.0006 | 0.7370 | 0.0693 | 0.0502 | 0.1556 |
| ppo_warmstart_step0/seed_001/trace.jsonl | 500 | 0.0361 | 2.2016 | 0.1742 | 0.1002 | 0.1556 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_000.jsonl | 500 | 0.0489 | 2.3112 | 0.1834 | 0.0990 | 0.1520 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_001.jsonl | 500 | 0.0455 | 2.3454 | 0.1850 | 0.0966 | 0.1556 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_002.jsonl | 500 | 0.0494 | 2.2580 | 0.1809 | 0.0972 | 0.1509 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_003.jsonl | 500 | 0.0439 | 2.2634 | 0.1824 | 0.1001 | 0.1554 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_004.jsonl | 500 | 0.0463 | 2.3584 | 0.1836 | 0.0972 | 0.1506 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_005.jsonl | 500 | 0.0489 | 2.3112 | 0.1835 | 0.1270 | 0.1462 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_006.jsonl | 500 | 0.0442 | 2.3178 | 0.1863 | 0.0963 | 0.1557 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_007.jsonl | 500 | 0.0457 | 2.3633 | 0.1847 | 0.0977 | 0.1557 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
