# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_023_history_context_resetsettle10/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `c40e85596f38a7d9`
- teacher_entries: `112`
- teacher_samples: `62437`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0038 | 0.0095 | 0.0138 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0037 | 0.0095 | 0.0138 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 430, 'double_support_low_progress': 254, 'low_progress': 254, 'reverse_velocity': 254, 'zero_command_drift': 131}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 430, 'double_support_low_progress': 254, 'low_progress': 254, 'reverse_velocity': 254, 'zero_command_drift': 135}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
