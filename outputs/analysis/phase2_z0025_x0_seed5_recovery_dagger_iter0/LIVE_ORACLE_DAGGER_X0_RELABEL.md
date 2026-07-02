# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`
- teacher_dataset_id: `e1d14b2c3f81d443`
- teacher_entries: `14`
- teacher_samples: `10500`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `1`
- samples_out: `43`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_005/trace.jsonl | 43 | 0 | 0.0434 | 0.1117 | 0.1860 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_005/trace.jsonl`: `{'double_support_low_progress': 33, 'high_lateral_velocity': 5, 'high_tracking_error': 3, 'low_progress': 36, 'reverse_velocity': 36, 'zero_command_drift': 43}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
