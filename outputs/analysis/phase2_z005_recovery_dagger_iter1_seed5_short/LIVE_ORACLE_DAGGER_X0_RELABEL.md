# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- teacher_dataset_id: `d8498b665c201936`
- teacher_entries: `8`
- teacher_samples: `6000`
- teacher_model_kind: `zero_action`
- action_dim: `14`
- zero_action_alpha: `1.0`

## Summary

- traces: `1`
- samples_out: `61`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_005/trace.jsonl | 61 | 0 | 0.1674 | 0.5502 | 0.6690 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `rollouts_x0/student/seed_005/trace.jsonl`: `{'base': 1, 'double_support_low_progress': 44, 'high_lateral_velocity': 6, 'high_tracking_error': 4, 'low_progress': 49, 'reverse_velocity': 49, 'zero_command_drift': 59}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
