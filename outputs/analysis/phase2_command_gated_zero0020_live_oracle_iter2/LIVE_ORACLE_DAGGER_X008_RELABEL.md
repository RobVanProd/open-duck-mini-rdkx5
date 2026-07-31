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

- traces: `1`
- samples_out: `392`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_006/trace.jsonl | 392 | 0 | 0.0068 | 0.0309 | 0.3049 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_006/trace.jsonl`: `{'base': 109, 'double_support_low_progress': 129, 'high_lateral_velocity': 52, 'high_tracking_error': 186, 'low_progress': 187, 'reverse_velocity': 93}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
