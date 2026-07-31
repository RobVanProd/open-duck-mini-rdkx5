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
- samples_out: `1500`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 0 | 0.0065 | 0.0194 | 0.3347 | 5.0000 | 5.0000 |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 0 | 0.0060 | 0.0184 | 0.7208 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_000/trace.jsonl`: `{'base': 197, 'double_support_low_progress': 444, 'high_tracking_error': 4, 'low_progress': 445, 'reverse_velocity': 445, 'zero_command_drift': 248}`
- `rollouts_x0/student/seed_001/trace.jsonl`: `{'base': 386, 'double_support_low_progress': 277, 'high_lateral_velocity': 10, 'high_tracking_error': 4, 'low_progress': 277, 'reverse_velocity': 277, 'zero_command_drift': 190}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
