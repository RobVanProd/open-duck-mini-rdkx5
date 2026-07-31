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

- traces: `2`
- samples_out: `500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 250 | 0 | 0.0184 | 0.0798 | 0.1135 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_004/trace.jsonl | 250 | 0 | 0.0202 | 0.0878 | 0.4001 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 95, 'double_support_low_progress': 140, 'high_lateral_velocity': 1, 'high_tracking_error': 3, 'low_progress': 142, 'reverse_velocity': 142, 'zero_command_drift': 26}`
- `rollouts_x0/student/seed_004/trace.jsonl`: `{'base': 71, 'double_support_low_progress': 122, 'high_lateral_velocity': 3, 'high_tracking_error': 3, 'low_progress': 122, 'reverse_velocity': 122, 'zero_command_drift': 78}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
