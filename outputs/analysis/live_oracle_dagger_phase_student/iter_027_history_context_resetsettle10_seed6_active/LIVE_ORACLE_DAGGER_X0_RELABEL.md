# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `55a6b9ee65b134d9`
- teacher_entries: `119`
- teacher_samples: `67219`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0022 | 0.0060 | 0.0087 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0022 | 0.0060 | 0.0090 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 423, 'double_support_low_progress': 262, 'low_progress': 262, 'reverse_velocity': 262, 'zero_command_drift': 126}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 425, 'double_support_low_progress': 259, 'low_progress': 259, 'reverse_velocity': 259, 'zero_command_drift': 130}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
