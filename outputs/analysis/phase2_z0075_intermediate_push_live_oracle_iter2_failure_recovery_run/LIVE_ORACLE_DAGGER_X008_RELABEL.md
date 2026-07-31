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

- traces: `5`
- samples_out: `1814`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_001/trace.jsonl | 560 | 0 | 0.0185 | 0.0778 | 0.7385 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 643 | 0 | 0.0242 | 0.1390 | 0.8074 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_003/trace.jsonl | 85 | 0 | 0.0506 | 0.1993 | 0.4485 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_004/trace.jsonl | 478 | 0 | 0.0230 | 0.1032 | 0.7856 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_005/trace.jsonl | 48 | 0 | 0.0871 | 0.4105 | 0.7127 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 156, 'double_support_low_progress': 202, 'high_lateral_velocity': 95, 'high_tracking_error': 224, 'low_progress': 299, 'reverse_velocity': 126}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 149, 'double_support_low_progress': 330, 'high_lateral_velocity': 74, 'high_tracking_error': 196, 'low_progress': 395, 'reverse_velocity': 217}`
- `rollouts_x008/student/seed_003/trace.jsonl`: `{'double_support_low_progress': 74, 'high_lateral_velocity': 3, 'high_tracking_error': 7, 'low_progress': 85, 'reverse_velocity': 82}`
- `rollouts_x008/student/seed_004/trace.jsonl`: `{'base': 128, 'double_support_low_progress': 259, 'high_lateral_velocity': 35, 'high_tracking_error': 106, 'low_progress': 305, 'reverse_velocity': 157}`
- `rollouts_x008/student/seed_005/trace.jsonl`: `{'base': 1, 'double_support_low_progress': 36, 'high_lateral_velocity': 2, 'high_tracking_error': 7, 'low_progress': 40, 'reverse_velocity': 40}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
