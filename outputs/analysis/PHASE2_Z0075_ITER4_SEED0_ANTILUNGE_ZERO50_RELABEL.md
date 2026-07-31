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
- zero_action_alpha: `0.5`

## Summary

- traces: `1`
- samples_out: `141`
- truncated_traces: `1`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| phase2_z0075_control_preserving_recovery_rate150_seed0_trace/iter4_control_preserving_rate150/seed_000/trace.jsonl | 141 | 0 | 0.1364 | 0.3789 | 0.4408 | 1.0000 | 1.0000 |

### Sample Weight Reasons

- `phase2_z0075_control_preserving_recovery_rate150_seed0_trace/iter4_control_preserving_rate150/seed_000/trace.jsonl`: `{'base': 141}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
