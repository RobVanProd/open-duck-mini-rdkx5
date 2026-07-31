# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `b539bb4793ffdd67`
- teacher_entries: `102`
- teacher_samples: `40500`
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
- samples_out: `1332`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_000/trace.jsonl | 750 | 0 | 0.0145 | 0.0843 | 0.6033 | 5.0000 | 5.0000 |
| rollouts_x008/student/seed_007/trace.jsonl | 582 | 0 | 0.0144 | 0.0800 | 0.8433 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_000/trace.jsonl`: `{'base': 162, 'double_support_low_progress': 349, 'high_lateral_velocity': 107, 'high_tracking_error': 300, 'low_progress': 476, 'reverse_velocity': 168}`
- `rollouts_x008/student/seed_007/trace.jsonl`: `{'base': 137, 'double_support_low_progress': 229, 'high_lateral_velocity': 95, 'high_tracking_error': 270, 'low_progress': 323, 'reverse_velocity': 123}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
