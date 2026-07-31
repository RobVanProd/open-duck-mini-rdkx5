# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`
- teacher_dataset_id: `f60e4de49b96fb4f`
- teacher_entries: `98`
- teacher_samples: `53834`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0041 | 0.0087 | 0.0185 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0041 | 0.0087 | 0.0177 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 387, 'double_support_low_progress': 287, 'low_progress': 287, 'reverse_velocity': 287, 'zero_command_drift': 143}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 474, 'double_support_low_progress': 179, 'low_progress': 179, 'reverse_velocity': 179, 'zero_command_drift': 147}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
