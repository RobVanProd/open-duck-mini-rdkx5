# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_command_gated_zero0020_bc_manifest.json`
- teacher_dataset_id: `24beb17ef0e1de02`
- teacher_entries: `10`
- teacher_samples: `7500`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0011 | 0.0030 | 0.0053 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0011 | 0.0032 | 0.0055 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 434, 'double_support_low_progress': 250, 'low_progress': 250, 'reverse_velocity': 250, 'zero_command_drift': 127}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 426, 'double_support_low_progress': 256, 'low_progress': 256, 'reverse_velocity': 256, 'zero_command_drift': 138}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
