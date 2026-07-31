# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- teacher_dataset_id: `d8498b665c201936`
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
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0 | 0.0060 | 0.0279 | 0.1692 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0 | 0.0062 | 0.0273 | 0.2038 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0 | 0.0058 | 0.0255 | 0.0922 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0 | 0.0059 | 0.0271 | 0.1228 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0 | 0.0060 | 0.0274 | 0.3274 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_005/trace.jsonl | 750 | 0 | 0.0062 | 0.0304 | 0.1073 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 750 | 0 | 0.0059 | 0.0272 | 0.1158 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0060 | 0.0314 | 0.2110 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 99, 'double_support_low_progress': 380, 'high_lateral_velocity': 67, 'high_tracking_error': 433, 'low_progress': 519, 'reverse_velocity': 95}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 110, 'double_support_low_progress': 327, 'high_lateral_velocity': 79, 'high_tracking_error': 453, 'low_progress': 474, 'reverse_velocity': 69}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 104, 'double_support_low_progress': 352, 'high_lateral_velocity': 71, 'high_tracking_error': 457, 'low_progress': 483, 'reverse_velocity': 50}`
- `rollouts_x008/student/seed_003/trace.jsonl`: `{'base': 94, 'double_support_low_progress': 396, 'high_lateral_velocity': 65, 'high_tracking_error': 434, 'low_progress': 511, 'reverse_velocity': 109}`
- `rollouts_x008/student/seed_004/trace.jsonl`: `{'base': 100, 'double_support_low_progress': 359, 'high_lateral_velocity': 69, 'high_tracking_error': 450, 'low_progress': 497, 'reverse_velocity': 81}`
- `rollouts_x008/student/seed_005/trace.jsonl`: `{'base': 88, 'double_support_low_progress': 400, 'high_lateral_velocity': 60, 'high_tracking_error': 437, 'low_progress': 517, 'reverse_velocity': 113}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 107, 'double_support_low_progress': 336, 'high_lateral_velocity': 78, 'high_tracking_error': 443, 'low_progress': 480, 'reverse_velocity': 91}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 105, 'double_support_low_progress': 373, 'high_lateral_velocity': 63, 'high_tracking_error': 427, 'low_progress': 492, 'reverse_velocity': 99}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
