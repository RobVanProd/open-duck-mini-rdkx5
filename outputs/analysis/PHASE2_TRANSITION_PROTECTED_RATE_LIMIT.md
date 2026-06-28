# Transition-Protected BC Trace Action Rate Limit

status: `PASS_TRANSITION_PROTECTED_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x008/rollouts_x008/student/seed_*/trace.jsonl']`
- output_trace_dir: `outputs/analysis/phase2_transition_protected_rate_limit_traces`
- joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- max_target_velocity_rad_s: `2.25`
- protect_transition_window_ticks: `6`
- protect_non_double_support: `True`
- protected_contacts: `[]`

## Summary

- traces: `2`
- samples_out: `500`
- protected_samples: `488`
- changed_ticks: `13`
- changed_contact_counts: `{'11': 13}`
- protected_contact_counts: `{'01': 96, '10': 68, '11': 324}`

| source | samples | protected | changed | joint | orig_p95 | limited_p95 | removed_p95 |
|---|---:|---:|---:|---|---:|---:|---:|
| trace.jsonl | 250 | 241 | 0 | `left_hip_pitch` | 1.8189 | 1.8189 | 0.0000 |
| trace.jsonl | 250 | 241 | 1 | `left_knee` | 2.7878 | 2.7878 | 0.0000 |
| trace.jsonl | 250 | 241 | 1 | `left_ankle` | 2.3709 | 2.3055 | 0.0000 |
| trace.jsonl | 250 | 241 | 1 | `right_hip_pitch` | 1.5587 | 1.5587 | 0.0000 |
| trace.jsonl | 250 | 241 | 7 | `right_knee` | 4.3007 | 4.0884 | 0.0000 |
| trace.jsonl | 250 | 241 | 1 | `right_ankle` | 2.7860 | 2.7139 | 0.0000 |
| trace.jsonl | 250 | 247 | 0 | `left_hip_pitch` | 2.0092 | 2.0092 | 0.0000 |
| trace.jsonl | 250 | 247 | 0 | `left_knee` | 2.8531 | 2.8531 | 0.0000 |
| trace.jsonl | 250 | 247 | 2 | `left_ankle` | 2.3891 | 2.3819 | 0.0000 |
| trace.jsonl | 250 | 247 | 0 | `right_hip_pitch` | 1.6627 | 1.6627 | 0.0000 |
| trace.jsonl | 250 | 247 | 0 | `right_knee` | 3.8269 | 3.8269 | 0.0000 |
| trace.jsonl | 250 | 247 | 0 | `right_ankle` | 2.1541 | 2.1541 | 0.0000 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
