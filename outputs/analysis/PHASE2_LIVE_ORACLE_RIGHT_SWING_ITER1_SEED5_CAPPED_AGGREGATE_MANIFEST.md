# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_seed4_right_swing_weighted_command_manifest.json`
- `outputs/analysis/phase2_live_oracle_right_swing_iter1_seed5_capped_x008_manifest.json`
- `outputs/analysis/phase2_live_oracle_right_swing_iter1/live_oracle_dagger_x0_manifest.json`

## Thresholds

- min_entries: `12`
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

- input_entries: `12`
- kept_entries: `12`
- rejected_entries: `0`
- samples: `3000`
- source_files: `12`
- max_source_fraction: `0.0833`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| phase2_seed4_right_swing_weighted_traces/phase2_transition_action_space_compare_seed4/transition_protected_seed4w/seed_004/trace.jsonl | 250 | 0.0335 | 1.9720 | 0.1682 | 0.1007 | 0.1506 |
| phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed2/transition_protected_seed4w/seed_002/trace.jsonl | 250 | 0.0409 | 1.9524 | 0.1662 | 0.1007 | 0.1511 |
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
