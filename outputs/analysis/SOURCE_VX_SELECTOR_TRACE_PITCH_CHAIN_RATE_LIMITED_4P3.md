# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/source_vx_selector_fitted_bridge_x008_10s_traces/*.jsonl']`
- output_trace_dir: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces`
- joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- max_target_velocity_rad_s: `4.3`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.344000`

## Summary

- traces: `8`
- samples_out: `4000`
- changed_ticks: `543`
- changed_contact_counts: `{'00': 1, '01': 1, '10': 217, '11': 324}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | 500 | 0 | `left_hip_pitch` | 2.3116 | 3.0838 | 2.3116 | 3.0838 | 0.0000 | 0.0000 |
| seed_000.jsonl | 500 | 0 | `left_knee` | 3.0915 | 4.0882 | 3.0915 | 4.0882 | 0.0000 | 0.0000 |
| seed_000.jsonl | 500 | 1 | `left_ankle` | 2.8843 | 4.3254 | 2.8843 | 4.3000 | 0.0000 | 0.0020 |
| seed_000.jsonl | 500 | 0 | `right_hip_pitch` | 1.7329 | 2.9458 | 1.7329 | 2.9458 | 0.0000 | 0.0000 |
| seed_000.jsonl | 500 | 62 | `right_knee` | 5.2058 | 7.4214 | 4.3000 | 4.3000 | 0.0962 | 0.2497 |
| seed_000.jsonl | 500 | 3 | `right_ankle` | 2.6779 | 5.1079 | 2.6948 | 4.3000 | 0.0000 | 0.0646 |
| seed_001.jsonl | 500 | 0 | `left_hip_pitch` | 2.3176 | 3.9204 | 2.3176 | 3.9204 | 0.0000 | 0.0000 |
| seed_001.jsonl | 500 | 0 | `left_knee` | 3.0006 | 4.0114 | 3.0006 | 4.0114 | 0.0000 | 0.0000 |
| seed_001.jsonl | 500 | 5 | `left_ankle` | 3.0444 | 5.5232 | 3.0444 | 4.3000 | 0.0000 | 0.0979 |
| seed_001.jsonl | 500 | 0 | `right_hip_pitch` | 1.7682 | 2.9179 | 1.7682 | 2.9179 | 0.0000 | 0.0000 |
| seed_001.jsonl | 500 | 62 | `right_knee` | 4.9479 | 7.4632 | 4.3000 | 4.3000 | 0.0938 | 0.2531 |
| seed_001.jsonl | 500 | 2 | `right_ankle` | 2.8627 | 5.7818 | 2.9741 | 4.3000 | 0.0000 | 0.1185 |
| seed_002.jsonl | 500 | 0 | `left_hip_pitch` | 2.3112 | 2.7162 | 2.3112 | 2.7162 | 0.0000 | 0.0000 |
| seed_002.jsonl | 500 | 0 | `left_knee` | 3.0915 | 4.0882 | 3.0915 | 4.0882 | 0.0000 | 0.0000 |
| seed_002.jsonl | 500 | 1 | `left_ankle` | 2.6521 | 4.8386 | 2.6521 | 4.3000 | 0.0000 | 0.0431 |
| seed_002.jsonl | 500 | 0 | `right_hip_pitch` | 1.8032 | 3.2867 | 1.8032 | 3.2867 | 0.0000 | 0.0000 |
| seed_002.jsonl | 500 | 63 | `right_knee` | 5.2255 | 6.8682 | 4.3000 | 4.3000 | 0.0959 | 0.2055 |
| seed_002.jsonl | 500 | 3 | `right_ankle` | 2.6548 | 5.1066 | 2.6548 | 4.3000 | 0.0000 | 0.0645 |
| seed_003.jsonl | 500 | 0 | `left_hip_pitch` | 2.3112 | 2.8018 | 2.3112 | 2.8018 | 0.0000 | 0.0000 |
| seed_003.jsonl | 500 | 1 | `left_knee` | 3.0915 | 4.6319 | 3.0915 | 4.3000 | 0.0000 | 0.0266 |
| seed_003.jsonl | 500 | 3 | `left_ankle` | 2.7491 | 5.5232 | 2.7491 | 4.3000 | 0.0000 | 0.0979 |
| seed_003.jsonl | 500 | 0 | `right_hip_pitch` | 1.8032 | 2.6969 | 1.8032 | 2.6969 | 0.0000 | 0.0000 |
| seed_003.jsonl | 500 | 63 | `right_knee` | 5.2451 | 5.9447 | 4.3000 | 4.3000 | 0.1006 | 0.1470 |
| seed_003.jsonl | 500 | 1 | `right_ankle` | 2.6548 | 4.3190 | 2.6548 | 4.3000 | 0.0000 | 0.0015 |
| seed_004.jsonl | 500 | 0 | `left_hip_pitch` | 2.3176 | 3.5645 | 2.3176 | 3.5645 | 0.0000 | 0.0000 |
| seed_004.jsonl | 500 | 1 | `left_knee` | 2.8180 | 4.9078 | 2.8180 | 4.3000 | 0.0000 | 0.0486 |
| seed_004.jsonl | 500 | 4 | `left_ankle` | 3.0931 | 5.5248 | 3.0931 | 4.3000 | 0.0000 | 0.0980 |
| seed_004.jsonl | 500 | 0 | `right_hip_pitch` | 1.7448 | 3.3443 | 1.7448 | 3.3443 | 0.0000 | 0.0000 |
| seed_004.jsonl | 500 | 62 | `right_knee` | 5.1439 | 8.3015 | 4.3000 | 4.3000 | 0.0871 | 0.3201 |
| seed_004.jsonl | 500 | 2 | `right_ankle` | 2.6548 | 5.7284 | 2.6638 | 4.3000 | 0.0000 | 0.1143 |
| seed_005.jsonl | 500 | 0 | `left_hip_pitch` | 2.3112 | 3.2347 | 2.3112 | 3.2347 | 0.0000 | 0.0000 |
| seed_005.jsonl | 500 | 2 | `left_knee` | 2.9885 | 7.2428 | 2.9971 | 4.3000 | 0.0000 | 0.2354 |
| seed_005.jsonl | 500 | 4 | `left_ankle` | 2.9595 | 5.5232 | 2.9860 | 4.3000 | 0.0000 | 0.0979 |
| seed_005.jsonl | 500 | 0 | `right_hip_pitch` | 1.7887 | 3.3425 | 1.7887 | 3.3425 | 0.0000 | 0.0000 |
| seed_005.jsonl | 500 | 58 | `right_knee` | 5.1850 | 6.3583 | 4.3000 | 4.3000 | 0.0990 | 0.1678 |
| seed_005.jsonl | 500 | 3 | `right_ankle` | 2.7734 | 5.2247 | 2.7750 | 4.3000 | 0.0000 | 0.0740 |
| seed_006.jsonl | 500 | 0 | `left_hip_pitch` | 2.3116 | 3.1347 | 2.3116 | 3.1347 | 0.0000 | 0.0000 |
| seed_006.jsonl | 500 | 2 | `left_knee` | 3.0915 | 4.6388 | 3.0915 | 4.3000 | 0.0000 | 0.0271 |
| seed_006.jsonl | 500 | 1 | `left_ankle` | 2.9967 | 5.5232 | 2.9967 | 4.3000 | 0.0000 | 0.0979 |
| seed_006.jsonl | 500 | 0 | `right_hip_pitch` | 1.8651 | 2.7928 | 1.8651 | 2.7928 | 0.0000 | 0.0000 |
| seed_006.jsonl | 500 | 61 | `right_knee` | 5.3054 | 7.7089 | 4.3000 | 4.3000 | 0.1086 | 0.2727 |
| seed_006.jsonl | 500 | 3 | `right_ankle` | 2.7437 | 6.1324 | 2.7605 | 4.3000 | 0.0000 | 0.1466 |
| seed_007.jsonl | 500 | 0 | `left_hip_pitch` | 2.3176 | 3.2437 | 2.3176 | 3.2437 | 0.0000 | 0.0000 |
| seed_007.jsonl | 500 | 1 | `left_knee` | 2.9757 | 4.9218 | 2.9757 | 4.3000 | 0.0000 | 0.0497 |
| seed_007.jsonl | 500 | 4 | `left_ankle` | 3.0136 | 4.8664 | 3.0955 | 4.3000 | 0.0000 | 0.0453 |
| seed_007.jsonl | 500 | 0 | `right_hip_pitch` | 1.7220 | 2.9243 | 1.7220 | 2.9243 | 0.0000 | 0.0000 |
| seed_007.jsonl | 500 | 62 | `right_knee` | 5.3072 | 7.7909 | 4.3000 | 4.3000 | 0.1034 | 0.2910 |
| seed_007.jsonl | 500 | 3 | `right_ankle` | 2.6684 | 5.9079 | 2.7246 | 4.3000 | 0.0000 | 0.1286 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
