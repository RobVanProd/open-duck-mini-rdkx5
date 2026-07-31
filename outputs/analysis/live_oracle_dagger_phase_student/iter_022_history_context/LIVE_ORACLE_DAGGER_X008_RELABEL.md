# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`
- teacher_dataset_id: `f60e4de49b96fb4f`
- teacher_entries: `187`
- teacher_samples: `53834`
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
- samples_out: `2594`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 115 | 0 | 0.0136 | 0.0617 | 0.1724 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 229 | 0 | 0.0109 | 0.0474 | 0.1875 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0 | 0.0095 | 0.0374 | 0.1108 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0 | 0.0099 | 0.0385 | 0.1396 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0090 | 0.0361 | 0.1165 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 50, 'double_support_low_progress': 33, 'high_lateral_velocity': 6, 'high_tracking_error': 41, 'low_progress': 34, 'reverse_velocity': 12}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 71, 'double_support_low_progress': 83, 'high_lateral_velocity': 28, 'high_tracking_error': 95, 'low_progress': 109, 'reverse_velocity': 44}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 214, 'double_support_low_progress': 265, 'high_lateral_velocity': 123, 'high_tracking_error': 312, 'low_progress': 400, 'reverse_velocity': 173}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 186, 'double_support_low_progress': 321, 'high_lateral_velocity': 93, 'high_tracking_error': 330, 'low_progress': 437, 'reverse_velocity': 182}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 195, 'double_support_low_progress': 305, 'high_lateral_velocity': 122, 'high_tracking_error': 312, 'low_progress': 459, 'reverse_velocity': 195}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
