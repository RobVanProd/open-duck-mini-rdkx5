# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_022_history_context/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `78dd40db3626cc2a`
- teacher_entries: `201`
- teacher_samples: `57928`
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
- samples_out: `3009`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 639 | 0 | 0.0091 | 0.0368 | 0.3890 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0 | 0.0091 | 0.0367 | 0.3890 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0 | 0.0085 | 0.0353 | 0.3890 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 120 | 0 | 0.0104 | 0.0505 | 0.3890 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0089 | 0.0362 | 0.3890 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 127, 'double_support_low_progress': 290, 'high_lateral_velocity': 108, 'high_tracking_error': 300, 'low_progress': 419, 'reverse_velocity': 186}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 189, 'double_support_low_progress': 261, 'high_lateral_velocity': 143, 'high_tracking_error': 372, 'low_progress': 402, 'reverse_velocity': 176}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 186, 'double_support_low_progress': 254, 'high_lateral_velocity': 113, 'high_tracking_error': 359, 'low_progress': 415, 'reverse_velocity': 157}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 47, 'double_support_low_progress': 35, 'high_lateral_velocity': 4, 'high_tracking_error': 49, 'low_progress': 40, 'reverse_velocity': 11}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 176, 'double_support_low_progress': 312, 'high_lateral_velocity': 101, 'high_tracking_error': 344, 'low_progress': 454, 'reverse_velocity': 160}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
