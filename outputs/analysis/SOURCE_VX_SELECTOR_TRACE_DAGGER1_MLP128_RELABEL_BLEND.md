# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/source_vx_selector_fitted_bridge_trace_manifest.json`
- teacher_dataset_id: `de4935ec7672ceea`
- teacher_entries: `8`
- teacher_samples: `4000`
- teacher_model_kind: `blend`
- knn_k: `5`
- blend_alpha: `0.8`
- best_alpha: `0.01`

## Summary

- traces: `8`
- samples_out: `3602`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max |
|---|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 0 | 0.0150 | 0.0551 | 0.1936 |
| seed_001.jsonl | 500 | 0 | 0.0141 | 0.0525 | 0.1627 |
| seed_002.jsonl | 500 | 0 | 0.0149 | 0.0556 | 0.2046 |
| seed_003.jsonl | 500 | 0 | 0.0173 | 0.0620 | 0.1792 |
| seed_004.jsonl | 500 | 0 | 0.0148 | 0.0530 | 0.1720 |
| seed_005.jsonl | 102 | 0 | 0.0279 | 0.1394 | 0.3642 |
| seed_006.jsonl | 500 | 0 | 0.0149 | 0.0547 | 0.1801 |
| seed_007.jsonl | 500 | 0 | 0.0150 | 0.0541 | 0.2323 |

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
