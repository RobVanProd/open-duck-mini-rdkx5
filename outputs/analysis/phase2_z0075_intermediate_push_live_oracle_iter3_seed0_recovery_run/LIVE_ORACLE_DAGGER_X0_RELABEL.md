# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `ad1f4a6a5446d648`
- teacher_entries: `68`
- teacher_samples: `48815`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0041 | 0.0099 | 0.0292 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0040 | 0.0103 | 0.0292 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 355, 'double_support_low_progress': 319, 'low_progress': 319, 'reverse_velocity': 319, 'zero_command_drift': 133}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 470, 'double_support_low_progress': 183, 'low_progress': 183, 'reverse_velocity': 183, 'zero_command_drift': 145}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
