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

- traces: `1`
- samples_out: `55`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_005/trace.jsonl | 55 | 0 | 0.0482 | 0.3030 | 0.8681 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_005/trace.jsonl`: `{'base': 2, 'double_support_low_progress': 39, 'high_lateral_velocity': 11, 'high_tracking_error': 21, 'low_progress': 47, 'reverse_velocity': 45}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
