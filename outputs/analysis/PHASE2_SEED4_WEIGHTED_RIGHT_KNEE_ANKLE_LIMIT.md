# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/phase2_seed4_weighted_right_knee_limited_traces/*/transition_protected_seed4w/seed_*/trace.jsonl']`
- output_trace_dir: `outputs/analysis/phase2_seed4_weighted_right_knee_ankle_limited_traces`
- joints: `['right_ankle']`
- max_target_velocity_rad_s: `2.0`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.160000`

## Summary

- traces: `2`
- samples_out: `500`
- changed_ticks: `54`
- changed_contact_counts: `{'10': 2, '11': 52}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| trace.jsonl | 250 | 27 | `right_ankle` | 2.2510 | 3.1234 | 2.0000 | 2.0000 | 0.0595 | 0.1301 |
| trace.jsonl | 250 | 27 | `right_ankle` | 2.2936 | 2.8278 | 2.0000 | 2.0000 | 0.0556 | 0.1198 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
