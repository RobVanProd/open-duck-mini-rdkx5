# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_z0075_iter10_spike_local_merged_manifest.json`
- teacher_dataset_id: `0c16a7273cf0fbdc`
- teacher_entries: `157`
- teacher_samples: `52924`
- teacher_model_kind: `source_vx_blend`
- knn_k: `5`
- blend_alpha: `0.8`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `0.02`
- source_vx_threshold_m_s: `0.02`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `seed_004`
- best_alpha: `1e-06`

## Summary

- traces: `4`
- samples_out: `175`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl | 61 | 0 | 0.0110 | 0.0718 | 0.2412 | 4.0000 | 5.0000 |
| phase2_z0075_home_support_push_window_snippets/seed_002/push_009_e969257189933035.jsonl | 42 | 0 | 0.0132 | 0.0517 | 0.1039 | 5.0000 | 5.0000 |
| phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl | 64 | 0 | 0.0127 | 0.0624 | 0.1243 | 5.0000 | 5.0000 |
| phase2_z0075_home_support_push_window_snippets/seed_006/push_011_420a187c0ff36573.jsonl | 8 | 0 | 0.0307 | 0.0811 | 0.1243 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl`: `{'base': 21, 'double_support_low_progress': 10, 'high_lateral_velocity': 8, 'high_tracking_error': 30, 'low_progress': 10, 'reverse_velocity': 1}`
- `phase2_z0075_home_support_push_window_snippets/seed_002/push_009_e969257189933035.jsonl`: `{'double_support_low_progress': 38, 'high_lateral_velocity': 4, 'high_tracking_error': 11, 'low_progress': 42, 'reverse_velocity': 42}`
- `phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl`: `{'double_support_low_progress': 48, 'high_lateral_velocity': 13, 'high_tracking_error': 23, 'low_progress': 64, 'reverse_velocity': 60}`
- `phase2_z0075_home_support_push_window_snippets/seed_006/push_011_420a187c0ff36573.jsonl`: `{'double_support_low_progress': 5, 'high_lateral_velocity': 4, 'high_tracking_error': 1, 'low_progress': 8, 'reverse_velocity': 8}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
