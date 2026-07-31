# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `55a6b9ee65b134d9`
- teacher_entries: `229`
- teacher_samples: `67219`
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
- samples_out: `3250`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0 | 0.0083 | 0.0343 | 0.2686 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0 | 0.0083 | 0.0331 | 0.2686 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0 | 0.0083 | 0.0342 | 0.2686 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 250 | 0 | 0.0093 | 0.0397 | 0.2686 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0084 | 0.0356 | 0.2686 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 166, 'double_support_low_progress': 328, 'high_lateral_velocity': 96, 'high_tracking_error': 335, 'low_progress': 469, 'reverse_velocity': 221}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 198, 'double_support_low_progress': 290, 'high_lateral_velocity': 114, 'high_tracking_error': 317, 'low_progress': 420, 'reverse_velocity': 191}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 195, 'double_support_low_progress': 303, 'high_lateral_velocity': 110, 'high_tracking_error': 324, 'low_progress': 444, 'reverse_velocity': 196}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 54, 'double_support_low_progress': 122, 'high_lateral_velocity': 29, 'high_tracking_error': 93, 'low_progress': 173, 'reverse_velocity': 119}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 172, 'double_support_low_progress': 333, 'high_lateral_velocity': 92, 'high_tracking_error': 342, 'low_progress': 466, 'reverse_velocity': 199}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
