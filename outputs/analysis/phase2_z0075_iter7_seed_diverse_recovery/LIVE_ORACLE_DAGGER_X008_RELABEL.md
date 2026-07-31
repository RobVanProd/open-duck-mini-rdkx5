# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `b539bb4793ffdd67`
- teacher_entries: `102`
- teacher_samples: `40500`
- teacher_model_kind: `source_vx_blend`
- knn_k: `5`
- blend_alpha: `0.8`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `0.02`
- source_vx_threshold_m_s: `0.02`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `seed_004`
- best_alpha: `1e-06`

## Summary

- traces: `6`
- samples_out: `2112`
- truncated_traces: `6`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_001/trace.jsonl | 493 | 0 | 0.0126 | 0.0555 | 0.2004 | 5.0000 | 5.0000 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_002/trace.jsonl | 156 | 0 | 0.0145 | 0.0857 | 0.5365 | 5.0000 | 5.0000 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_003/trace.jsonl | 449 | 0 | 0.0132 | 0.0633 | 0.6669 | 5.0000 | 5.0000 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl | 723 | 0 | 0.0128 | 0.0542 | 0.3402 | 5.0000 | 5.0000 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_005/trace.jsonl | 46 | 0 | 0.0400 | 0.1771 | 0.3704 | 5.0000 | 5.0000 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_006/trace.jsonl | 245 | 0 | 0.0145 | 0.0850 | 0.3421 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_001/trace.jsonl`: `{'base': 94, 'double_support_low_progress': 224, 'high_lateral_velocity': 92, 'high_tracking_error': 211, 'low_progress': 316, 'reverse_velocity': 183}`
- `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_002/trace.jsonl`: `{'base': 46, 'double_support_low_progress': 44, 'high_lateral_velocity': 21, 'high_tracking_error': 76, 'low_progress': 58, 'reverse_velocity': 29}`
- `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_003/trace.jsonl`: `{'base': 70, 'double_support_low_progress': 260, 'high_lateral_velocity': 61, 'high_tracking_error': 171, 'low_progress': 331, 'reverse_velocity': 190}`
- `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 282, 'high_lateral_velocity': 70, 'high_tracking_error': 315, 'low_progress': 383, 'reverse_velocity': 167}`
- `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_005/trace.jsonl`: `{'double_support_low_progress': 31, 'high_lateral_velocity': 10, 'high_tracking_error': 9, 'low_progress': 39, 'reverse_velocity': 37}`
- `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_006/trace.jsonl`: `{'base': 51, 'double_support_low_progress': 131, 'high_lateral_velocity': 30, 'high_tracking_error': 74, 'low_progress': 175, 'reverse_velocity': 112}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
