# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_023_history_context_resetsettle10/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `c40e85596f38a7d9`
- teacher_entries: `215`
- teacher_samples: `62437`
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

- traces: `5`
- samples_out: `3282`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0 | 0.0087 | 0.0356 | 0.3029 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0 | 0.0087 | 0.0357 | 0.3029 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 282 | 0 | 0.0091 | 0.0374 | 0.3029 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0 | 0.0088 | 0.0350 | 0.3029 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0085 | 0.0337 | 0.3029 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 187, 'double_support_low_progress': 294, 'high_lateral_velocity': 105, 'high_tracking_error': 334, 'low_progress': 428, 'reverse_velocity': 168}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 186, 'double_support_low_progress': 293, 'high_lateral_velocity': 111, 'high_tracking_error': 344, 'low_progress': 437, 'reverse_velocity': 181}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 43, 'double_support_low_progress': 158, 'high_lateral_velocity': 31, 'high_tracking_error': 114, 'low_progress': 219, 'reverse_velocity': 120}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 190, 'double_support_low_progress': 306, 'high_lateral_velocity': 94, 'high_tracking_error': 326, 'low_progress': 444, 'reverse_velocity': 199}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 161, 'double_support_low_progress': 321, 'high_lateral_velocity': 97, 'high_tracking_error': 344, 'low_progress': 467, 'reverse_velocity': 180}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
