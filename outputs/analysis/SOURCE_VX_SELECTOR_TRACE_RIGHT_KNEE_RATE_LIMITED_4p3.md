# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_selector_fitted_bridge_x008_10s_traces/*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces`
- joints: `['right_knee']`
- max_target_velocity_rad_s: `4.3`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.344000`

## Summary

- traces: `8`
- samples_out: `4000`
- changed_ticks: `493`
- changed_contact_counts: `{'10': 216, '11': 277}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 62 | `right_knee` | 5.2058 | 7.4214 | 4.3000 | 4.3000 | 0.0962 | 0.2497 |
| seed_001.jsonl | 500 | 62 | `right_knee` | 4.9479 | 7.4632 | 4.3000 | 4.3000 | 0.0938 | 0.2531 |
| seed_002.jsonl | 500 | 63 | `right_knee` | 5.2255 | 6.8682 | 4.3000 | 4.3000 | 0.0959 | 0.2055 |
| seed_003.jsonl | 500 | 63 | `right_knee` | 5.2451 | 5.9447 | 4.3000 | 4.3000 | 0.1006 | 0.1470 |
| seed_004.jsonl | 500 | 62 | `right_knee` | 5.1439 | 8.3015 | 4.3000 | 4.3000 | 0.0871 | 0.3201 |
| seed_005.jsonl | 500 | 58 | `right_knee` | 5.1850 | 6.3583 | 4.3000 | 4.3000 | 0.0990 | 0.1678 |
| seed_006.jsonl | 500 | 61 | `right_knee` | 5.3054 | 7.7089 | 4.3000 | 4.3000 | 0.1086 | 0.2727 |
| seed_007.jsonl | 500 | 62 | `right_knee` | 5.3072 | 7.7909 | 4.3000 | 4.3000 | 0.1034 | 0.2910 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
