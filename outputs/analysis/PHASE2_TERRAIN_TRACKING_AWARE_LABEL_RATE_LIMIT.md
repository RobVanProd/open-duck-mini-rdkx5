# BC Trace Action Rate Limit

status: `PASS_BC_TRACE_ACTION_RATE_LIMIT_READY`

This is an offline dataset-curation artifact. It does not run robot tests, SSH, deploy, train, or change runtime behavior.

## Settings

- trace_globs: `['outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/relabel_x008/rollouts_x008/student/seed_*/trace.jsonl']`
- output_trace_dir: `outputs/analysis/phase2_terrain_tracking_aware_labels/rate_limited_x008`
- joints: `['left_hip_pitch', 'left_knee', 'left_ankle', 'right_hip_pitch', 'right_knee', 'right_ankle']`
- max_target_velocity_rad_s: `2.25`
- action_scale: `0.25`
- dt_s: `0.02`
- max_action_delta: `0.180000`

## Summary

- traces: `2`
- samples_out: `500`
- changed_ticks: `343`
- changed_contact_counts: `{'01': 28, '10': 57, '11': 258}`

| source | samples | changed | joint | orig_p95 | orig_max | limited_p95 | limited_max | removed_p95 | removed_max |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| trace.jsonl | 250 | 1 | `left_hip_pitch` | 1.8189 | 4.3739 | 1.8189 | 2.2500 | 0.0000 | 0.1699 |
| trace.jsonl | 250 | 41 | `left_knee` | 2.7878 | 3.9559 | 2.2500 | 2.2500 | 0.0616 | 0.1406 |
| trace.jsonl | 250 | 19 | `left_ankle` | 2.3709 | 4.4691 | 2.2500 | 2.2500 | 0.0344 | 0.1775 |
| trace.jsonl | 250 | 6 | `right_hip_pitch` | 1.5587 | 3.0811 | 1.6198 | 2.2500 | 0.0000 | 0.0665 |
| trace.jsonl | 250 | 70 | `right_knee` | 4.3007 | 7.8378 | 2.2500 | 2.2500 | 0.3253 | 0.5716 |
| trace.jsonl | 250 | 31 | `right_ankle` | 2.7860 | 4.6282 | 2.2500 | 2.2500 | 0.0530 | 0.1903 |
| trace.jsonl | 250 | 8 | `left_hip_pitch` | 2.0092 | 3.4732 | 2.0346 | 2.2500 | 0.0000 | 0.1533 |
| trace.jsonl | 250 | 39 | `left_knee` | 2.8531 | 3.9140 | 2.2500 | 2.2500 | 0.0730 | 0.1757 |
| trace.jsonl | 250 | 22 | `left_ankle` | 2.3891 | 3.6927 | 2.2500 | 2.2500 | 0.0382 | 0.1154 |
| trace.jsonl | 250 | 6 | `right_hip_pitch` | 1.6627 | 3.0284 | 1.7330 | 2.2500 | 0.0000 | 0.0623 |
| trace.jsonl | 250 | 80 | `right_knee` | 3.8269 | 7.8409 | 2.2500 | 2.2500 | 0.3090 | 0.4659 |
| trace.jsonl | 250 | 20 | `right_ankle` | 2.1541 | 4.7729 | 2.2500 | 2.2500 | 0.0493 | 0.2018 |

## Gate

- Raw output JSONL traces remain ignored unless explicitly force-added.
- This only edits offline training/eval traces; it is not a runtime smoother.
- Any student trained from these traces still requires closed-loop multi-seed gates.
