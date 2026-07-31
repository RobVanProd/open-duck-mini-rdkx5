# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_seed4_right_swing_weighted_command_manifest.json`
- teacher_dataset_id: `b86c263a03fa826f`
- teacher_entries: `3`
- teacher_samples: `750`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `1`
- samples_out: `42`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| phase2_seed5_capped_neighbor_trace_compare_x0/seed5_capped/seed_005/trace.jsonl | 42 | 0 | 0.0313 | 0.2348 | 0.5267 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `phase2_seed5_capped_neighbor_trace_compare_x0/seed5_capped/seed_005/trace.jsonl`: `{'double_support_low_progress': 29, 'high_lateral_velocity': 5, 'high_tracking_error': 3, 'low_progress': 36, 'reverse_velocity': 36, 'zero_command_drift': 41}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
