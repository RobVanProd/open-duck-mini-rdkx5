# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json`
- teacher_dataset_id: `7e8f2e0e92557f8b`
- teacher_entries: `38`
- teacher_samples: `28500`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `8`
- samples_out: `6000`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_002/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_003/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_004/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_005/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_006/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_007/trace.jsonl | 750 | 0 | 0.0064 | 0.0212 | 0.0336 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`
- `rollouts_x0/student/seed_002/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`
- `rollouts_x0/student/seed_003/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`
- `rollouts_x0/student/seed_004/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`
- `rollouts_x0/student/seed_005/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`
- `rollouts_x0/student/seed_006/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`
- `rollouts_x0/student/seed_007/trace.jsonl`: `{'base': 575, 'double_support_low_progress': 175, 'low_progress': 175, 'reverse_velocity': 175, 'zero_command_drift': 10}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
