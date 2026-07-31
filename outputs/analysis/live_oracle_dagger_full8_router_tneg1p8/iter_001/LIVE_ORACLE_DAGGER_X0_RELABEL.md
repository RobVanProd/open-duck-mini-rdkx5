# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest.json`
- teacher_dataset_id: `e6d3c1def23826e4`
- teacher_entries: `16`
- teacher_samples: `12000`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0023 | 0.0066 | 0.0109 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0023 | 0.0066 | 0.0103 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 402, 'double_support_low_progress': 281, 'low_progress': 281, 'reverse_velocity': 281, 'zero_command_drift': 125}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 421, 'double_support_low_progress': 264, 'low_progress': 264, 'reverse_velocity': 264, 'zero_command_drift': 131}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
