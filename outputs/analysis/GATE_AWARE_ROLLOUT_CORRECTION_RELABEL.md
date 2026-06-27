# BC Trace Relabel

status: `PASS_BC_TRACE_RELABEL_READY`

This offline artifact relabels student-visited observations with a teacher action.
Raw JSONL outputs remain ignored and are referenced only for local follow-up.

## Teacher

- teacher_manifest: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- teacher_dataset_id: `3aedbacc4a592fc8`
- teacher_entries: `15`
- teacher_samples: `4000`
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
- samples_out: `1000`
- truncated_traces: `0`

| source | samples_out | skipped | action_delta_p50 | action_delta_p95 | action_delta_max | weight_p95 | weight_max |
|---|---:|---:|---:|---:|---:|---:|---:|
| ppo_warmstart_restore_policy_kl100_640/seed_001/trace.jsonl | 500 | 0 | 0.1342 | 0.3541 | 0.5782 | 5.0000 | 5.0000 |
| ppo_warmstart_step0/seed_001/trace.jsonl | 500 | 0 | 0.0196 | 0.0761 | 0.3538 | 5.0000 | 5.0000 |

### Sample Weight Reasons

- `ppo_warmstart_restore_policy_kl100_640/seed_001/trace.jsonl`: `{'base': 5, 'double_support_low_progress': 483, 'high_lateral_velocity': 9, 'high_tracking_error': 10, 'low_progress': 494, 'reverse_velocity': 247}`
- `ppo_warmstart_step0/seed_001/trace.jsonl`: `{'base': 76, 'double_support_low_progress': 160, 'high_lateral_velocity': 42, 'high_tracking_error': 322, 'low_progress': 298, 'reverse_velocity': 64}`

## Gate

- Do not commit raw relabeled JSONL traces unless explicitly approved.
- Use the output traces only for offline distillation experiments.
