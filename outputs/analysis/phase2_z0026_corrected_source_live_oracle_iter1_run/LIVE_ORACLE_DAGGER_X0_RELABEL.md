# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json`
- teacher_dataset_id: `0d4c2e82ef0ff64e`
- teacher_entries: `8`
- teacher_samples: `6000`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0358 | 0.1143 | 0.1301 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0358 | 0.1143 | 0.1301 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 66, 'double_support_low_progress': 382, 'low_progress': 382, 'reverse_velocity': 382, 'zero_command_drift': 592}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 66, 'double_support_low_progress': 382, 'low_progress': 382, 'reverse_velocity': 382, 'zero_command_drift': 592}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
