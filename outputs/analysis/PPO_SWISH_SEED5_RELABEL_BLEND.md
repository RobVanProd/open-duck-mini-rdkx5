# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- teacher_dataset_id: `80ea809b021b6b9a`
- teacher_entries: `25`
- teacher_samples: `9268`
- teacher_model_kind: `blend`
- knn_k: `5`
- blend_alpha: `0.8`
- best_alpha: `1e-06`

## Summary

- traces: `1`
- samples_out: `74`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max |
|---|---:|---:|---:|---:|---:|
| trace.jsonl | 74 | 0 | 0.0244 | 0.1097 | 0.4297 |

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
