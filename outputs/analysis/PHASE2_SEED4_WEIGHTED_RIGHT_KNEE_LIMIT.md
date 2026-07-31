# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/phase2_transition_action_space_compare_seed2/transition_protected_seed4w/seed_*/trace.jsonl', 'outputs/analysis/phase2_transition_action_space_compare_seed4/transition_protected_seed4w/seed_*/trace.jsonl']`
- output_trace_dir: `outputs/analysis/phase2_seed4_weighted_right_knee_limited_traces`
- joints: `['right_knee']`
- max_target_velocity_rad_s: `2.25`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.180000`

## Summary

- traces: `2`
- samples_out: `500`
- changed_ticks: `130`
- changed_contact_counts: `{'01': 2, '10': 28, '11': 100}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| trace.jsonl | 250 | 62 | `right_knee` | 2.9950 | 3.5938 | 2.2500 | 2.2500 | 0.1572 | 0.2884 |
| trace.jsonl | 250 | 68 | `right_knee` | 2.8552 | 3.4080 | 2.2500 | 2.2500 | 0.1402 | 0.2505 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
