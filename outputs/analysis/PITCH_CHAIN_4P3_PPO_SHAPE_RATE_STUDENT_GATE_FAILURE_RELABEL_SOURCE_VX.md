# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- teacher_dataset_id: `407af2cbe0ad69e1`
- teacher_entries: `499`
- teacher_samples: `6475`
- teacher_model_kind: `source_vx_blend`
- knn_k: `5`
- blend_alpha: `0.8`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `-0.02`
- source_vx_threshold_m_s: `0.02`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `_seed4/`
- best_alpha: `1.0`

## Summary

- traces: `2`
- samples_out: `1000`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max |
|---|---:|---:|---:|---:|---:|
| seed_001/trace.jsonl | 500 | 0 | 0.0211 | 0.0848 | 0.3325 |
| seed_004/trace.jsonl | 500 | 0 | 0.0224 | 0.0968 | 0.3593 |

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
