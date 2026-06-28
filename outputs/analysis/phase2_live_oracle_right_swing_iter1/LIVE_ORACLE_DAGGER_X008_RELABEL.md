# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_seed4_right_swing_weighted_command_manifest.json`
- teacher_dataset_id: `b86c263a03fa826f`
- teacher_entries: `5`
- teacher_samples: `750`
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
- samples_out: `2000`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 250 | 0 | 0.1064 | 0.2544 | 0.4865 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 250 | 0 | 0.0698 | 0.2341 | 0.6635 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 250 | 0 | 0.0134 | 0.0628 | 0.3965 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_003/trace.jsonl | 250 | 0 | 0.0146 | 0.0653 | 0.5819 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_004/trace.jsonl | 250 | 0 | 0.0151 | 0.0615 | 0.6957 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_005/trace.jsonl | 250 | 0 | 0.0933 | 0.2485 | 0.4837 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 250 | 0 | 0.0159 | 0.0725 | 0.6435 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 250 | 0 | 0.0804 | 0.2404 | 0.6935 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 6, 'double_support_low_progress': 242, 'high_tracking_error': 3, 'low_progress': 244, 'reverse_velocity': 96}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 13, 'double_support_low_progress': 220, 'high_lateral_velocity': 20, 'high_tracking_error': 12, 'low_progress': 228, 'reverse_velocity': 104}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 41, 'double_support_low_progress': 87, 'high_lateral_velocity': 45, 'high_tracking_error': 138, 'low_progress': 129, 'reverse_velocity': 14}`
- `rollouts_x008/student/seed_003/trace.jsonl`: `{'base': 43, 'double_support_low_progress': 104, 'high_lateral_velocity': 34, 'high_tracking_error': 149, 'low_progress': 144, 'reverse_velocity': 33}`
- `rollouts_x008/student/seed_004/trace.jsonl`: `{'base': 33, 'double_support_low_progress': 128, 'high_lateral_velocity': 21, 'high_tracking_error': 149, 'low_progress': 164, 'reverse_velocity': 30}`
- `rollouts_x008/student/seed_005/trace.jsonl`: `{'base': 23, 'double_support_low_progress': 219, 'high_lateral_velocity': 6, 'high_tracking_error': 6, 'low_progress': 220, 'reverse_velocity': 102}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 46, 'double_support_low_progress': 104, 'high_lateral_velocity': 30, 'high_tracking_error': 137, 'low_progress': 143, 'reverse_velocity': 44}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 11, 'double_support_low_progress': 231, 'high_lateral_velocity': 5, 'high_tracking_error': 7, 'low_progress': 235, 'reverse_velocity': 106}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
