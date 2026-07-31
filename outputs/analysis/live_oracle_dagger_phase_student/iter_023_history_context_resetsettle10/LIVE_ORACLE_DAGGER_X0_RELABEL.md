# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_022_history_context/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `78dd40db3626cc2a`
- teacher_entries: `105`
- teacher_samples: `57928`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0024 | 0.0046 | 0.0088 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0024 | 0.0046 | 0.0084 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 429, 'double_support_low_progress': 255, 'low_progress': 255, 'reverse_velocity': 255, 'zero_command_drift': 128}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 416, 'double_support_low_progress': 267, 'low_progress': 267, 'reverse_velocity': 267, 'zero_command_drift': 136}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
