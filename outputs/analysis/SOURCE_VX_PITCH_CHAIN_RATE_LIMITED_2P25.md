# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_selector_fitted_bridge_x008_10s_traces/*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_pitch_chain_rate_limited_2p25_traces`
- joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- max_target_velocity_rad_s: `2.25`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.180000`

## Summary

- traces: `8`
- samples_out: `4000`
- changed_ticks: `3577`
- changed_contact_counts: `{'00': 9, '01': 463, '10': 882, '11': 2223}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 33 | `left_hip_pitch` | 2.3116 | 3.0838 | 2.2500 | 2.2500 | 0.0049 | 0.0526 |
| seed_000.jsonl | 500 | 102 | `left_knee` | 3.0915 | 4.0882 | 2.2500 | 2.2500 | 0.1107 | 0.2202 |
| seed_000.jsonl | 500 | 61 | `left_ankle` | 2.8843 | 4.3254 | 2.2500 | 2.2500 | 0.0962 | 0.2327 |
| seed_000.jsonl | 500 | 18 | `right_hip_pitch` | 1.7329 | 2.9458 | 1.7614 | 2.2500 | 0.0000 | 0.0557 |
| seed_000.jsonl | 500 | 171 | `right_knee` | 5.2058 | 7.4214 | 2.2500 | 2.2500 | 0.4485 | 0.6237 |
| seed_000.jsonl | 500 | 52 | `right_ankle` | 2.6779 | 5.1079 | 2.2500 | 2.2500 | 0.0922 | 0.3056 |
| seed_001.jsonl | 500 | 39 | `left_hip_pitch` | 2.3176 | 3.9204 | 2.2500 | 2.2500 | 0.0054 | 0.1326 |
| seed_001.jsonl | 500 | 106 | `left_knee` | 3.0006 | 4.0114 | 2.2500 | 2.2500 | 0.1054 | 0.1637 |
| seed_001.jsonl | 500 | 65 | `left_ankle` | 3.0444 | 5.5232 | 2.2500 | 2.2500 | 0.1017 | 0.2815 |
| seed_001.jsonl | 500 | 18 | `right_hip_pitch` | 1.7682 | 2.9179 | 1.7682 | 2.2500 | 0.0000 | 0.0534 |
| seed_001.jsonl | 500 | 176 | `right_knee` | 4.9479 | 7.4632 | 2.2500 | 2.2500 | 0.4434 | 0.5859 |
| seed_001.jsonl | 500 | 54 | `right_ankle` | 2.8627 | 5.7818 | 2.2500 | 2.2500 | 0.1541 | 0.3056 |
| seed_002.jsonl | 500 | 33 | `left_hip_pitch` | 2.3112 | 2.7162 | 2.2500 | 2.2500 | 0.0049 | 0.0373 |
| seed_002.jsonl | 500 | 100 | `left_knee` | 3.0915 | 4.0882 | 2.2500 | 2.2500 | 0.1075 | 0.1490 |
| seed_002.jsonl | 500 | 54 | `left_ankle` | 2.6521 | 4.8386 | 2.2500 | 2.2500 | 0.0819 | 0.2071 |
| seed_002.jsonl | 500 | 18 | `right_hip_pitch` | 1.8032 | 3.2867 | 1.8032 | 2.2500 | 0.0000 | 0.0829 |
| seed_002.jsonl | 500 | 173 | `right_knee` | 5.2255 | 6.8682 | 2.2500 | 2.2500 | 0.4509 | 0.5626 |
| seed_002.jsonl | 500 | 54 | `right_ankle` | 2.6548 | 5.1066 | 2.2500 | 2.2500 | 0.1422 | 0.3127 |
| seed_003.jsonl | 500 | 33 | `left_hip_pitch` | 2.3112 | 2.8018 | 2.2500 | 2.2500 | 0.0049 | 0.0441 |
| seed_003.jsonl | 500 | 105 | `left_knee` | 3.0915 | 4.6319 | 2.2500 | 2.2500 | 0.1135 | 0.2463 |
| seed_003.jsonl | 500 | 57 | `left_ankle` | 2.7491 | 5.5232 | 2.2500 | 2.2500 | 0.0856 | 0.2619 |
| seed_003.jsonl | 500 | 17 | `right_hip_pitch` | 1.8032 | 2.6969 | 1.8032 | 2.2500 | 0.0000 | 0.0357 |
| seed_003.jsonl | 500 | 175 | `right_knee` | 5.2451 | 5.9447 | 2.2500 | 2.2500 | 0.4474 | 0.4977 |
| seed_003.jsonl | 500 | 51 | `right_ankle` | 2.6548 | 4.3190 | 2.2500 | 2.2500 | 0.1416 | 0.3056 |
| seed_004.jsonl | 500 | 34 | `left_hip_pitch` | 2.3176 | 3.5645 | 2.2500 | 2.2500 | 0.0054 | 0.1052 |
| seed_004.jsonl | 500 | 97 | `left_knee` | 2.8180 | 4.9078 | 2.2500 | 2.2500 | 0.1098 | 0.2173 |
| seed_004.jsonl | 500 | 60 | `left_ankle` | 3.0931 | 5.5248 | 2.2500 | 2.2500 | 0.1301 | 0.4054 |
| seed_004.jsonl | 500 | 21 | `right_hip_pitch` | 1.7448 | 3.3443 | 1.7720 | 2.2500 | 0.0000 | 0.0875 |
| seed_004.jsonl | 500 | 182 | `right_knee` | 5.1439 | 8.3015 | 2.2500 | 2.2500 | 0.4424 | 0.5969 |
| seed_004.jsonl | 500 | 49 | `right_ankle` | 2.6548 | 5.7284 | 2.2500 | 2.2500 | 0.1267 | 0.3056 |
| seed_005.jsonl | 500 | 33 | `left_hip_pitch` | 2.3112 | 3.2347 | 2.2500 | 2.2500 | 0.0049 | 0.0788 |
| seed_005.jsonl | 500 | 118 | `left_knee` | 2.9885 | 7.2428 | 2.2500 | 2.2500 | 0.1026 | 0.3994 |
| seed_005.jsonl | 500 | 61 | `left_ankle` | 2.9595 | 5.5232 | 2.2500 | 2.2500 | 0.1320 | 0.2776 |
| seed_005.jsonl | 500 | 19 | `right_hip_pitch` | 1.7887 | 3.3425 | 1.7887 | 2.2500 | 0.0000 | 0.0874 |
| seed_005.jsonl | 500 | 175 | `right_knee` | 5.1850 | 6.3583 | 2.2500 | 2.2500 | 0.4406 | 0.4958 |
| seed_005.jsonl | 500 | 54 | `right_ankle` | 2.7734 | 5.2247 | 2.2500 | 2.2500 | 0.1263 | 0.2551 |
| seed_006.jsonl | 500 | 35 | `left_hip_pitch` | 2.3116 | 3.1347 | 2.2500 | 2.2500 | 0.0049 | 0.0708 |
| seed_006.jsonl | 500 | 100 | `left_knee` | 3.0915 | 4.6388 | 2.2500 | 2.2500 | 0.1066 | 0.2463 |
| seed_006.jsonl | 500 | 61 | `left_ankle` | 2.9967 | 5.5232 | 2.2500 | 2.2500 | 0.1118 | 0.2619 |
| seed_006.jsonl | 500 | 22 | `right_hip_pitch` | 1.8651 | 2.7928 | 1.8782 | 2.2500 | 0.0000 | 0.0434 |
| seed_006.jsonl | 500 | 175 | `right_knee` | 5.3054 | 7.7089 | 2.2500 | 2.2500 | 0.4503 | 0.6276 |
| seed_006.jsonl | 500 | 53 | `right_ankle` | 2.7437 | 6.1324 | 2.2500 | 2.2500 | 0.1394 | 0.3106 |
| seed_007.jsonl | 500 | 42 | `left_hip_pitch` | 2.3176 | 3.2437 | 2.2500 | 2.2500 | 0.0054 | 0.0795 |
| seed_007.jsonl | 500 | 107 | `left_knee` | 2.9757 | 4.9218 | 2.2500 | 2.2500 | 0.1012 | 0.2158 |
| seed_007.jsonl | 500 | 65 | `left_ankle` | 3.0136 | 4.8664 | 2.2500 | 2.2500 | 0.1459 | 0.2456 |
| seed_007.jsonl | 500 | 19 | `right_hip_pitch` | 1.7220 | 2.9243 | 1.7443 | 2.2500 | 0.0000 | 0.0539 |
| seed_007.jsonl | 500 | 174 | `right_knee` | 5.3072 | 7.7909 | 2.2500 | 2.2500 | 0.4549 | 0.6190 |
| seed_007.jsonl | 500 | 56 | `right_ankle` | 2.6684 | 5.9079 | 2.2500 | 2.2500 | 0.1144 | 0.2926 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
