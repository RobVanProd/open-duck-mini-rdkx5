# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_selector_fitted_bridge_x008_10s_traces/*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces`
- joints: `['right_knee']`
- max_target_velocity_rad_s: `4.7`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.376000`

## Summary

- traces: `8`
- samples_out: `4000`
- changed_ticks: `408`
- changed_contact_counts: `{'10': 199, '11': 209}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 48 | `right_knee` | 5.2058 | 7.4214 | 4.7000 | 4.7000 | 0.0492 | 0.2177 |
| seed_001.jsonl | 500 | 47 | `right_knee` | 4.9479 | 7.4632 | 4.7000 | 4.7000 | 0.0483 | 0.2211 |
| seed_002.jsonl | 500 | 52 | `right_knee` | 5.2255 | 6.8682 | 4.7000 | 4.7000 | 0.0520 | 0.1735 |
| seed_003.jsonl | 500 | 52 | `right_knee` | 5.2451 | 5.9447 | 4.7000 | 4.7000 | 0.0518 | 0.0996 |
| seed_004.jsonl | 500 | 52 | `right_knee` | 5.1439 | 8.3015 | 4.7000 | 4.7000 | 0.0483 | 0.2881 |
| seed_005.jsonl | 500 | 48 | `right_knee` | 5.1850 | 6.3583 | 4.7000 | 4.7000 | 0.0573 | 0.1327 |
| seed_006.jsonl | 500 | 56 | `right_knee` | 5.3054 | 7.7089 | 4.7000 | 4.7000 | 0.0585 | 0.2407 |
| seed_007.jsonl | 500 | 53 | `right_knee` | 5.3072 | 7.7909 | 4.7000 | 4.7000 | 0.0534 | 0.2473 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
