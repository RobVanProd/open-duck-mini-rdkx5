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

- traces: `2`
- samples_out: `147`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_006/push_002_d58ee50a26422599.jsonl | 74 | 0 | 0.0163 | 0.0666 | 0.2922 | 2.0000 | 2.0000 |
| analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_007/push_007_0083b1968111b80b.jsonl | 73 | 0 | 0.0152 | 0.0696 | 0.1515 | 2.0000 | 2.0000 |

### Sample Weight Reasons

- `analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_006/push_002_d58ee50a26422599.jsonl`: `{'base': 49, 'double_support_low_progress': 3, 'high_lateral_velocity': 3, 'high_tracking_error': 20, 'low_progress': 7, 'reverse_velocity': 2}`
- `analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_007/push_007_0083b1968111b80b.jsonl`: `{'base': 42, 'double_support_low_progress': 5, 'high_tracking_error': 31, 'low_progress': 6}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
