# Filtered BC Manifest

status: `PASS_FILTERED_BC_MANIFEST_READY`

This is an offline manifest curation artifact. It does not train, deploy, SSH, or touch the robot.

## Inputs

- `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_manifest.json`
- `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_x0_manifest.json`

## Thresholds

- min_entries: `3`
- min_samples: `100`
- min_mean_vx: `-0.01`
- max_vy_abs_p95: `0.25`
- max_pitch_abs_p95: `0.25`
- min_base_height: `0.12`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.2`
- require_bc_ready: `True`
- require_raw_trace: `True`
- reject_done_inside: `True`

## Summary

- input_entries: `3`
- kept_entries: `3`
- rejected_entries: `0`
- samples: `750`
- source_files: `3`
- max_source_fraction: `0.3333`

### Rejection Reasons

| reason | count |
|---|---:|

### Kept Entries

| source | samples | vx | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---:|---:|---:|---:|
| phase2_seed4_weighted_knee_ankle_leftknee_limited_traces/phase2_seed4_weighted_right_knee_ankle_limited_traces/phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed2/transition_protected_seed4w/seed_002/trace.jsonl | 250 | 0.0409 | 1.9524 | 0.1662 | 0.1007 | 0.1511 |
| phase2_seed4_weighted_knee_ankle_leftknee_limited_traces/phase2_seed4_weighted_right_knee_ankle_limited_traces/phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed4/transition_protected_seed4w/seed_004/trace.jsonl | 250 | 0.0335 | 1.9720 | 0.1682 | 0.1007 | 0.1506 |
| rollouts_x0/student/seed_000/trace.jsonl | 250 | -0.0010 | 0.2511 | 0.0365 | 0.0457 | 0.1519 |

## Gate

- Kept entries are suitable as positive BC labels for the next supervised fit.
- Rejected entries may still be useful for failure analysis, but should not be used as positive action labels.
