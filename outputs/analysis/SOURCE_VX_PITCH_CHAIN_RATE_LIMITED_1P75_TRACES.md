# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_pitch_chain_rate_limited_2p25_traces/seed_*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_pitch_chain_rate_limited_1p75_traces`
- joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- max_target_velocity_rad_s: `1.75`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.140000`

## Summary

- traces: `8`
- samples_out: `4000`
- changed_ticks: `6059`
- changed_contact_counts: `{'00': 12, '01': 1040, '10': 1291, '11': 3716}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 90 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0400 |
| seed_000.jsonl | 500 | 221 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1029 | 0.1600 |
| seed_000.jsonl | 500 | 97 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0831 | 0.1600 |
| seed_000.jsonl | 500 | 44 | `right_hip_pitch` | 1.7614 | 2.2500 | 1.7500 | 1.7500 | 0.0208 | 0.0408 |
| seed_000.jsonl | 500 | 196 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1983 | 0.2782 |
| seed_000.jsonl | 500 | 94 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0804 | 0.1600 |
| seed_001.jsonl | 500 | 95 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0800 |
| seed_001.jsonl | 500 | 225 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1045 | 0.1724 |
| seed_001.jsonl | 500 | 114 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0942 | 0.1600 |
| seed_001.jsonl | 500 | 47 | `right_hip_pitch` | 1.7682 | 2.2500 | 1.7500 | 1.7500 | 0.0235 | 0.0411 |
| seed_001.jsonl | 500 | 201 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.2000 | 0.2782 |
| seed_001.jsonl | 500 | 85 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1200 | 0.1600 |
| seed_002.jsonl | 500 | 79 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0400 |
| seed_002.jsonl | 500 | 207 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1029 | 0.1610 |
| seed_002.jsonl | 500 | 92 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0800 | 0.1600 |
| seed_002.jsonl | 500 | 49 | `right_hip_pitch` | 1.8032 | 2.2500 | 1.7500 | 1.7500 | 0.0234 | 0.0800 |
| seed_002.jsonl | 500 | 192 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.2000 | 0.2679 |
| seed_002.jsonl | 500 | 97 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0800 | 0.1600 |
| seed_003.jsonl | 500 | 85 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0400 |
| seed_003.jsonl | 500 | 222 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1044 | 0.1744 |
| seed_003.jsonl | 500 | 94 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1015 | 0.1600 |
| seed_003.jsonl | 500 | 46 | `right_hip_pitch` | 1.8032 | 2.2500 | 1.7500 | 1.7500 | 0.0238 | 0.0425 |
| seed_003.jsonl | 500 | 211 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.2000 | 0.2619 |
| seed_003.jsonl | 500 | 91 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0800 | 0.1600 |
| seed_004.jsonl | 500 | 95 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0524 |
| seed_004.jsonl | 500 | 230 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1086 | 0.2000 |
| seed_004.jsonl | 500 | 99 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0989 | 0.1600 |
| seed_004.jsonl | 500 | 45 | `right_hip_pitch` | 1.7720 | 2.2500 | 1.7500 | 1.7500 | 0.0252 | 0.0836 |
| seed_004.jsonl | 500 | 215 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.2000 | 0.2704 |
| seed_004.jsonl | 500 | 91 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0865 | 0.1600 |
| seed_005.jsonl | 500 | 86 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0816 |
| seed_005.jsonl | 500 | 222 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1181 | 0.1914 |
| seed_005.jsonl | 500 | 97 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0804 | 0.1600 |
| seed_005.jsonl | 500 | 43 | `right_hip_pitch` | 1.7887 | 2.2500 | 1.7500 | 1.7500 | 0.0227 | 0.0800 |
| seed_005.jsonl | 500 | 218 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.2000 | 0.2665 |
| seed_005.jsonl | 500 | 93 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0822 | 0.1600 |
| seed_006.jsonl | 500 | 96 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0536 |
| seed_006.jsonl | 500 | 220 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1039 | 0.1600 |
| seed_006.jsonl | 500 | 101 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0991 | 0.1600 |
| seed_006.jsonl | 500 | 52 | `right_hip_pitch` | 1.8782 | 2.2500 | 1.7500 | 1.7500 | 0.0297 | 0.0523 |
| seed_006.jsonl | 500 | 216 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.2000 | 0.2612 |
| seed_006.jsonl | 500 | 88 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1021 | 0.1600 |
| seed_007.jsonl | 500 | 95 | `left_hip_pitch` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0400 | 0.0495 |
| seed_007.jsonl | 500 | 239 | `left_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1197 | 0.1856 |
| seed_007.jsonl | 500 | 109 | `left_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1024 | 0.1686 |
| seed_007.jsonl | 500 | 40 | `right_hip_pitch` | 1.7443 | 2.2500 | 1.7500 | 1.7500 | 0.0295 | 0.0434 |
| seed_007.jsonl | 500 | 204 | `right_knee` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.1969 | 0.2576 |
| seed_007.jsonl | 500 | 91 | `right_ankle` | 2.2500 | 2.2500 | 1.7500 | 1.7500 | 0.0822 | 0.1600 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
