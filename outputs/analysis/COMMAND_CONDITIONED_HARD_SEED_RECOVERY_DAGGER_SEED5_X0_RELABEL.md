# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_manifest.json`
- teacher_dataset_id: `c9f8db0fac6d0022`
- teacher_entries: `19`
- teacher_samples: `10250`
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

- traces: `1`
- samples_out: `72`
- truncated_traces: `1`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max |
|---|---:|---:|---:|---:|---:|
| seed_005/trace.jsonl | 72 | 0 | 0.0194 | 0.1005 | 0.2867 |

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
