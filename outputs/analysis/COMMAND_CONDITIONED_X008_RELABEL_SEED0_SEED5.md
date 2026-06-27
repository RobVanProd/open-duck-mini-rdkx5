# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_manifest.json`
- teacher_dataset_id: `7877cd6345c6e333`
- teacher_entries: `20`
- teacher_samples: `10322`
- teacher_model_kind: `blend`
- knn_k: `5`
- blend_alpha: `0.8`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `0.02`
- source_vx_threshold_m_s: `0.02`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- best_alpha: `1e-06`

## Summary

- traces: `2`
- samples_out: `1000`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max |
|---|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 500 | 0 | 0.0094 | 0.0394 | 0.1388 |
| seed_005/trace.jsonl | 500 | 0 | 0.0104 | 0.0542 | 0.2424 |

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
