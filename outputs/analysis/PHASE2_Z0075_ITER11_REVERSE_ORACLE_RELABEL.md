# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/phase2_phase1_rate175_z0026_x008_source_manifest.json`
- teacher_dataset_id: `0d4c2e82ef0ff64e`
- teacher_entries: `15`
- teacher_samples: `6000`
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
- best_alpha: `0.01`

## Summary

- traces: `2`
- samples_out: `462`
- truncated_traces: `2`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_001/trace.jsonl | 418 | 0 | 0.0126 | 0.0478 | 0.1971 | 6.0000 | 6.0000 |
| phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_005/trace.jsonl | 44 | 0 | 0.0276 | 0.1683 | 0.4039 | 6.0000 | 6.0000 |

### Sample Weight Reasons

- `phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_001/trace.jsonl`: `{'base': 87, 'double_support_low_progress': 167, 'high_lateral_velocity': 91, 'high_tracking_error': 182, 'low_progress': 265, 'reverse_velocity': 144}`
- `phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_005/trace.jsonl`: `{'base': 1, 'double_support_low_progress': 30, 'high_lateral_velocity': 9, 'high_tracking_error': 10, 'low_progress': 37, 'reverse_velocity': 35}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
