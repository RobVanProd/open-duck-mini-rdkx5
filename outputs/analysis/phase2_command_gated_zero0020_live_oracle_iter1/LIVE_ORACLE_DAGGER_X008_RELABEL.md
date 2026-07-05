# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_command_gated_zero0020_bc_manifest.json`
- teacher_dataset_id: `24beb17ef0e1de02`
- teacher_entries: `20`
- teacher_samples: `7500`
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
- samples_out: `1413`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 663 | 0 | 0.0072 | 0.0282 | 0.2337 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 750 | 0 | 0.0077 | 0.0316 | 0.2579 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 154, 'double_support_low_progress': 308, 'high_lateral_velocity': 91, 'high_tracking_error': 268, 'low_progress': 423, 'reverse_velocity': 220}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 139, 'double_support_low_progress': 405, 'high_lateral_velocity': 84, 'high_tracking_error': 293, 'low_progress': 517, 'reverse_velocity': 241}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
