# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json`
- teacher_dataset_id: `0d4c2e82ef0ff64e`
- teacher_entries: `15`
- teacher_samples: `6000`
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
- best_alpha: `0.01`

## Summary

- traces: `8`
- samples_out: `6000`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_005/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0000 | 0.0034 | 0.0129 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`
- `rollouts_x008/student/seed_003/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`
- `rollouts_x008/student/seed_004/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`
- `rollouts_x008/student/seed_005/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 174, 'double_support_low_progress': 290, 'high_lateral_velocity': 133, 'high_tracking_error': 388, 'low_progress': 441, 'reverse_velocity': 125}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
