# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/phase2_seed4_weighted_right_knee_ankle_limited_traces/*/*/transition_protected_seed4w/seed_*/trace.jsonl']`
- output_trace_dir: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limited_traces`
- joints: `['left_knee']`
- max_target_velocity_rad_s: `2.25`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.180000`

## Summary

- traces: `2`
- samples_out: `500`
- changed_ticks: `47`
- changed_contact_counts: `{'01': 12, '10': 10, '11': 25}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| trace.jsonl | 250 | 18 | `left_knee` | 2.2628 | 2.8269 | 2.2500 | 2.2500 | 0.0027 | 0.0462 |
| trace.jsonl | 250 | 29 | `left_knee` | 2.3298 | 2.9564 | 2.2500 | 2.2500 | 0.0157 | 0.0565 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
