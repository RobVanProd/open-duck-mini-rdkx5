# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_selector_fitted_bridge_x008_10s_traces/*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces`
- joints: `['right_knee']`
- max_target_velocity_rad_s: `4.0`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.320000`

## Summary

- traces: `8`
- samples_out: `4000`
- changed_ticks: `642`
- changed_contact_counts: `{'00': 1, '01': 6, '10': 277, '11': 358}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 80 | `right_knee` | 5.2058 | 7.4214 | 4.0000 | 4.0000 | 0.1330 | 0.2737 |
| seed_001.jsonl | 500 | 78 | `right_knee` | 4.9479 | 7.4632 | 4.0000 | 4.0000 | 0.1231 | 0.2771 |
| seed_002.jsonl | 500 | 83 | `right_knee` | 5.2255 | 6.8682 | 4.0000 | 4.0000 | 0.1344 | 0.2295 |
| seed_003.jsonl | 500 | 80 | `right_knee` | 5.2451 | 5.9447 | 4.0000 | 4.0000 | 0.1373 | 0.1950 |
| seed_004.jsonl | 500 | 79 | `right_knee` | 5.1439 | 8.3015 | 4.0000 | 4.0000 | 0.1278 | 0.3441 |
| seed_005.jsonl | 500 | 80 | `right_knee` | 5.1850 | 6.3583 | 4.0000 | 4.0000 | 0.1305 | 0.2158 |
| seed_006.jsonl | 500 | 82 | `right_knee` | 5.3054 | 7.7089 | 4.0000 | 4.0000 | 0.1517 | 0.2967 |
| seed_007.jsonl | 500 | 80 | `right_knee` | 5.3072 | 7.7909 | 4.0000 | 4.0000 | 0.1507 | 0.3390 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
