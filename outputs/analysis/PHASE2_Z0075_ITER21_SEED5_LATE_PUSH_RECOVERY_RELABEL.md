# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `ddbeda5b717074b6`
- teacher_entries: `137`
- teacher_samples: `51175`
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
- samples_out: `79`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| analysis/phase2_z0075_iter21_seed5_late_push_recovery_snippets/seed_005/push_009_200a8ce383346549.jsonl | 79 | 0 | 0.0204 | 0.0869 | 0.3296 | 8.0000 | 8.0000 |

### Sample Weight Reasons

- `analysis/phase2_z0075_iter21_seed5_late_push_recovery_snippets/seed_005/push_009_200a8ce383346549.jsonl`: `{'base': 1, 'double_support_low_progress': 64, 'high_lateral_velocity': 2, 'high_tracking_error': 15, 'low_progress': 78, 'reverse_velocity': 70}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
