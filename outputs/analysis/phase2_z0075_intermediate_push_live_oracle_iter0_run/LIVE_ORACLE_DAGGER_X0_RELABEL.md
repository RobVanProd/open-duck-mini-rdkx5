# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `b539bb4793ffdd67`
- teacher_entries: `54`
- teacher_samples: `40500`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `812`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 62 | 0 | 0.0924 | 0.4670 | 0.8632 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0063 | 0.0293 | 0.5264 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'double_support_low_progress': 47, 'high_lateral_velocity': 2, 'high_tracking_error': 11, 'low_progress': 54, 'reverse_velocity': 54, 'zero_command_drift': 62}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 376, 'double_support_low_progress': 296, 'high_lateral_velocity': 9, 'high_tracking_error': 2, 'low_progress': 298, 'reverse_velocity': 298, 'zero_command_drift': 165}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
