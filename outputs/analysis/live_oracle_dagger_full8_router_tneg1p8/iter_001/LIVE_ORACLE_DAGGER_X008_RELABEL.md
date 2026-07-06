# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest.json`
- teacher_dataset_id: `e6d3c1def23826e4`
- teacher_entries: `30`
- teacher_samples: `12000`
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

- traces: `8`
- samples_out: `5336`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0 | 0.0069 | 0.0249 | 0.0745 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_001/trace.jsonl | 750 | 0 | 0.0062 | 0.0222 | 0.0647 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_002/trace.jsonl | 750 | 0 | 0.0066 | 0.0243 | 0.0732 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_003/trace.jsonl | 750 | 0 | 0.0066 | 0.0236 | 0.0873 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_004/trace.jsonl | 750 | 0 | 0.0063 | 0.0234 | 0.0681 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_005/trace.jsonl | 154 | 0 | 0.0064 | 0.0484 | 0.3187 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_006/trace.jsonl | 682 | 0 | 0.0068 | 0.0273 | 0.4206 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0065 | 0.0246 | 0.1066 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 165, 'double_support_low_progress': 360, 'high_lateral_velocity': 100, 'high_tracking_error': 340, 'low_progress': 474, 'reverse_velocity': 223}`
- `rollouts_x008/student/seed_001/trace.jsonl`: `{'base': 180, 'double_support_low_progress': 330, 'high_lateral_velocity': 93, 'high_tracking_error': 339, 'low_progress': 464, 'reverse_velocity': 239}`
- `rollouts_x008/student/seed_002/trace.jsonl`: `{'base': 144, 'double_support_low_progress': 386, 'high_lateral_velocity': 85, 'high_tracking_error': 332, 'low_progress': 507, 'reverse_velocity': 225}`
- `rollouts_x008/student/seed_003/trace.jsonl`: `{'base': 167, 'double_support_low_progress': 356, 'high_lateral_velocity': 98, 'high_tracking_error': 335, 'low_progress': 479, 'reverse_velocity': 220}`
- `rollouts_x008/student/seed_004/trace.jsonl`: `{'base': 164, 'double_support_low_progress': 337, 'high_lateral_velocity': 104, 'high_tracking_error': 334, 'low_progress': 465, 'reverse_velocity': 224}`
- `rollouts_x008/student/seed_005/trace.jsonl`: `{'base': 56, 'double_support_low_progress': 63, 'high_lateral_velocity': 9, 'high_tracking_error': 63, 'low_progress': 69, 'reverse_velocity': 21}`
- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 162, 'double_support_low_progress': 321, 'high_lateral_velocity': 52, 'high_tracking_error': 285, 'low_progress': 419, 'reverse_velocity': 199}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 164, 'double_support_low_progress': 332, 'high_lateral_velocity': 81, 'high_tracking_error': 325, 'low_progress': 466, 'reverse_velocity': 217}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
