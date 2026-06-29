# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_seed5_early_state_aggregate_manifest.json`
- `outputs/analysis/phase2_seed5_x008_neighbor_recovery_manifest.json`
- `outputs/analysis/phase2_seed5_x0_neighbor_recovery_manifest.json`

## Thresholds

- min_entries: `1`
- min_samples: `1`
- min_mean_vx: `-999.0`
- max_vy_abs_p95: `999.0`
- max_pitch_abs_p95: `999.0`
- min_base_height: `-999.0`
- max_sent_velocity_p95: `999.0`
- max_tracking_p95: `999.0`
- include_source_regex: `None`
- exclude_source_regex: `phase2_seed5_early_state_x0_curated_traces|phase2_seed5_early_state_x008_curated_traces`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `16`
- kept_entries: `16`
- rejected_entries: `0`
- samples: `3086`
- source_files: `16`
- max_source_fraction: `0.0625`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| phase2_seed4_right_swing_weighted_traces/phase2_transition_action_space_compare_seed4/transition_protected_seed4w/seed_004/trace.jsonl | 250 | 0.0335 | 1.9720 | 0.1682 | 0.1007 | 0.1506 |
| phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed2/transition_protected_seed4w/seed_002/trace.jsonl | 250 | 0.0409 | 1.9524 | 0.1662 | 0.1007 | 0.1511 |
| phase2_seed5_capped_neighbor_trace_compare_x0/seed5_capped/seed_005/trace.jsonl | 18 | -0.0233 | 1.7669 | 0.1450 | 0.2172 | 0.1468 |
| phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_005/trace.jsonl | 25 | 0.0201 | 1.8359 | 0.1652 | 0.2202 | 0.1465 |
| phase2_seed5_neighbor_recovery_traces/x008_seed5_neighbor_recovery/trace.jsonl | 25 | 0.0201 | 1.8359 | 0.1652 | 0.2202 | 0.1465 |
| phase2_seed5_neighbor_recovery_traces/x0_seed5_neighbor_recovery/trace.jsonl | 18 | -0.0233 | 1.7669 | 0.1450 | 0.2172 | 0.1468 |
| relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 250 | -0.0010 | 0.2511 | 0.0365 | 0.0457 | 0.1519 |
| rollouts_x0/student/seed_000/trace.jsonl | 250 | -0.0005 | 0.0918 | 0.0286 | 0.0222 | 0.1520 |
| rollouts_x0/student/seed_004/trace.jsonl | 250 | 0.0032 | 0.1099 | 0.0301 | 0.0350 | 0.1507 |
| rollouts_x008/student/seed_000/trace.jsonl | 250 | 0.0021 | 0.2865 | 0.0429 | 0.0289 | 0.1519 |
| rollouts_x008/student/seed_001/trace.jsonl | 250 | 0.0049 | 0.8511 | 0.0728 | 0.0617 | 0.1563 |
| rollouts_x008/student/seed_002/trace.jsonl | 250 | 0.0409 | 1.7609 | 0.1527 | 0.1108 | 0.1511 |
| rollouts_x008/student/seed_003/trace.jsonl | 250 | 0.0315 | 1.8475 | 0.1561 | 0.1271 | 0.1555 |
| rollouts_x008/student/seed_005/trace.jsonl | 250 | 0.0101 | 0.5049 | 0.0530 | 0.1558 | 0.1464 |
| rollouts_x008/student/seed_006/trace.jsonl | 250 | 0.0367 | 1.8006 | 0.1543 | 0.1204 | 0.1530 |
| rollouts_x008/student/seed_007/trace.jsonl | 250 | 0.0024 | 0.7948 | 0.0668 | 0.0498 | 0.1564 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
