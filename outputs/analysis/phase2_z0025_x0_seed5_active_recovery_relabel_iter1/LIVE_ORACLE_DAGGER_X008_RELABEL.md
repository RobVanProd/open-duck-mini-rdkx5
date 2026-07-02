# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `e1d14b2c3f81d443`
- teacher_entries: `26`
- teacher_samples: `10500`
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

- traces: `1`
- samples_out: `100`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x008/student/seed_005/trace.jsonl | 100 | 0 | 0.0113 | 0.0503 | 0.1129 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x008/student/seed_005/trace.jsonl`: `{'base': 25, 'double_support_low_progress': 51, 'high_lateral_velocity': 4, 'high_tracking_error': 39, 'low_progress': 56, 'reverse_velocity': 34}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
