# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `[]`
- manifests: `['outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/live_oracle_dagger_aggregate_manifest.json']`
- output_trace_dir: `outputs/analysis/phase2_iter2_right_ankle_limited198_traces`
- joints: `['right_ankle']`
- max_target_velocity_rad_s: `1.98`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.158400`

## Summary

- traces: `38`
- samples_out: `28500`
- changed_ticks: `288`
- changed_contact_counts: `{'01': 16, '10': 16, '11': 256}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 2 | `right_ankle` | 1.6027 | 2.0190 | 1.6027 | 1.9800 | 0.0000 | 0.0031 |
| trace.jsonl | 750 | 0 | `right_ankle` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| trace.jsonl | 750 | 0 | `right_ankle` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 18 | `right_ankle` | 1.6310 | 3.3807 | 1.6516 | 1.9800 | 0.0000 | 0.1121 |
| trace.jsonl | 750 | 0 | `right_ankle` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| trace.jsonl | 750 | 0 | `right_ankle` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 1 | `right_ankle` | 1.5909 | 1.9919 | 1.5909 | 1.9800 | 0.0000 | 0.0010 |
| trace.jsonl | 750 | 0 | `right_ankle` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| trace.jsonl | 750 | 0 | `right_ankle` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |
| trace.jsonl | 750 | 15 | `right_ankle` | 1.2876 | 6.5472 | 1.3508 | 1.9800 | 0.0000 | 0.3641 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
