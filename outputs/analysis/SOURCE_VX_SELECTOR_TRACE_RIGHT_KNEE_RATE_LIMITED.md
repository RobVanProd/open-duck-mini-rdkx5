# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_selector_fitted_bridge_x008_10s_traces/*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces`
- joints: `['right_knee']`
- max_target_velocity_rad_s: `3.75`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.300000`

## Summary

- traces: `8`
- samples_out: `4000`
- changed_ticks: `739`
- changed_contact_counts: `{'00': 1, '01': 6, '10': 351, '11': 381}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 91 | `right_knee` | 5.2058 | 7.4214 | 3.7500 | 3.7500 | 0.1708 | 0.2991 |
| seed_001.jsonl | 500 | 93 | `right_knee` | 4.9479 | 7.4632 | 3.7500 | 3.7500 | 0.1491 | 0.3015 |
| seed_002.jsonl | 500 | 92 | `right_knee` | 5.2255 | 6.8682 | 3.7500 | 3.7500 | 0.1716 | 0.2519 |
| seed_003.jsonl | 500 | 92 | `right_knee` | 5.2451 | 5.9447 | 3.7500 | 3.7500 | 0.1773 | 0.2350 |
| seed_004.jsonl | 500 | 92 | `right_knee` | 5.1439 | 8.3015 | 3.7500 | 3.7500 | 0.1673 | 0.3641 |
| seed_005.jsonl | 500 | 93 | `right_knee` | 5.1850 | 6.3583 | 3.7500 | 3.7500 | 0.1626 | 0.2558 |
| seed_006.jsonl | 500 | 94 | `right_knee` | 5.3054 | 7.7089 | 3.7500 | 3.7500 | 0.1908 | 0.3167 |
| seed_007.jsonl | 500 | 92 | `right_knee` | 5.3072 | 7.7909 | 3.7500 | 3.7500 | 0.1914 | 0.3790 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
