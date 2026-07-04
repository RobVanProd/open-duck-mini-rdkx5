# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `ad1f4a6a5446d648`
- teacher_entries: `129`
- teacher_samples: `48815`
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

- traces: `2`
- samples_out: `860`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 110 | 0 | 0.0120 | 0.0652 | 0.3971 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0115 | 0.0429 | 0.1543 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 41, 'double_support_low_progress': 28, 'high_lateral_velocity': 10, 'high_tracking_error': 49, 'low_progress': 32, 'reverse_velocity': 10}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 200, 'double_support_low_progress': 280, 'high_lateral_velocity': 102, 'high_tracking_error': 316, 'low_progress': 417, 'reverse_velocity': 153}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
