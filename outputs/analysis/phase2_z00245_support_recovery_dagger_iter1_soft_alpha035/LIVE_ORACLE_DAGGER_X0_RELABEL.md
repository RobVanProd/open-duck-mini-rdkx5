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
- blend_alpha: `0.35`
- vx_blend_alpha: `0.35`
- vx_blend_threshold_m_s: `0.02`
- source_vx_threshold_m_s: `0.02`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `seed_004`
- best_alpha: `0.01`

## Summary

- traces: `1`
- samples_out: `61`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_005/trace.jsonl | 61 | 0 | 0.0431 | 0.1378 | 0.3052 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_005/trace.jsonl`: `{'double_support_low_progress': 45, 'high_lateral_velocity': 6, 'high_tracking_error': 4, 'low_progress': 49, 'reverse_velocity': 49, 'zero_command_drift': 59}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
