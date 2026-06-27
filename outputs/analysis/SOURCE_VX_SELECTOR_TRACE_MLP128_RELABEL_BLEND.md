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
- samples_out: `1166`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max |
|---|---:|---:|---:|---:|---:|
| seed_000.jsonl | 162 | 0 | 0.1422 | 0.4755 | 0.8218 |
| seed_001.jsonl | 292 | 0 | 0.1455 | 0.4872 | 0.8783 |
| seed_002.jsonl | 93 | 0 | 0.1285 | 0.5325 | 0.8115 |
| seed_003.jsonl | 231 | 0 | 0.1408 | 0.4838 | 0.8263 |
| seed_004.jsonl | 102 | 0 | 0.1232 | 0.4678 | 0.8706 |
| seed_005.jsonl | 79 | 0 | 0.1180 | 0.4709 | 1.0982 |
| seed_006.jsonl | 117 | 0 | 0.1388 | 0.5034 | 0.9608 |
| seed_007.jsonl | 90 | 0 | 0.1315 | 0.4837 | 0.8059 |

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
