# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_health_routed_pass_parent_aggregate_manifest.json`
- `outputs/analysis/phase2_health_routed_parent_seed5_trace_manifest.json`

## Thresholds

- min_entries: `8`
- min_samples: `100`
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

- input_entries: `8`
- kept_entries: `8`
- rejected_entries: `0`
- samples: `6000`
- source_files: `8`
- max_source_fraction: `0.1250`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| phase2_health_routed_parent_ppo_step0_seed5_trace_compare/phase_parent/seed_005/trace.jsonl | 750 | 0.0296 | 1.4116 | 0.1393 | 0.1805 | 0.1588 |
| phase2_policy_route_trace_iter24_27/iter24/seed_000/trace.jsonl | 750 | 0.0261 | 1.4374 | 0.1398 | 0.1922 | 0.1591 |
| phase2_policy_route_trace_iter24_27/iter24/seed_002/trace.jsonl | 750 | 0.0262 | 1.4432 | 0.1397 | 0.1822 | 0.1590 |
| phase2_policy_route_trace_iter24_27/iter24/seed_007/trace.jsonl | 750 | 0.0275 | 1.4299 | 0.1405 | 0.1863 | 0.1565 |
| phase2_policy_route_trace_iter25_26/iter25/seed_001/trace.jsonl | 750 | 0.0285 | 1.4341 | 0.1413 | 0.1739 | 0.1579 |
| phase2_policy_route_trace_iter25_26/iter25/seed_006/trace.jsonl | 750 | 0.0262 | 1.4214 | 0.1407 | 0.1904 | 0.1580 |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0.0007 | 0.0086 | 0.0346 | 0.0629 | 0.1614 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0.0008 | 0.0085 | 0.0347 | 0.0658 | 0.1610 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
