# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/source_vx_selector_trace_dagger2_manifest.json`
- teacher_dataset_id: `29210cfbb880ecb9`
- teacher_entries: `24`
- teacher_samples: `8768`
- teacher_model_kind: `blend`
- knn_k: `5`
- blend_alpha: `0.8`
- best_alpha: `1e-06`

## Summary

- traces: `8`
- samples_out: `4000`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max |
|---|---:|---:|---:|---:|---:|
| trace.jsonl | 500 | 0 | 0.0172 | 0.0567 | 0.2075 |
| trace.jsonl | 500 | 0 | 0.0174 | 0.0575 | 0.2141 |
| trace.jsonl | 500 | 0 | 0.0172 | 0.0555 | 0.2084 |
| trace.jsonl | 500 | 0 | 0.0175 | 0.0613 | 0.2378 |
| trace.jsonl | 500 | 0 | 0.0168 | 0.0558 | 0.2006 |
| trace.jsonl | 500 | 0 | 0.0178 | 0.0582 | 0.1831 |
| trace.jsonl | 500 | 0 | 0.0170 | 0.0554 | 0.1981 |
| trace.jsonl | 500 | 0 | 0.0172 | 0.0577 | 0.2014 |

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
