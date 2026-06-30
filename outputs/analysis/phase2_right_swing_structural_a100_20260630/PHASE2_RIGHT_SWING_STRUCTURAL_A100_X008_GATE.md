# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0024`
min_swing_segments_per_foot: `2`
min_swing_rel_x_range_p95_m: `0.002`
min_swing_peak_lift_m: `0.002`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `right_swing_40960` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0198 | 0.2477 | 0.1230 | 0.1519 | 1.6369 | 0.0000 | 0.4487 | 0.1947 | 0.0138 | 11 | 0.0045 | 14.9333 | 85.0667 | 0 | NA |
| `right_swing_40960` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0207 | 0.2590 | 0.1201 | 0.1563 | 1.6541 | 0.0000 | 0.7447 | 0.1906 | 0.0113 | 11 | 0.0018 | 16.4000 | 83.4667 | 0 | NA |
| `right_swing_40960` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0225 | 0.2815 | 0.1250 | 0.1511 | 1.6757 | 0.0000 | 0.2686 | 0.1904 | 0.0130 | 9 | 0.0051 | 16.5333 | 83.4667 | 0 | NA |
| `right_swing_40960` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0161 | 0.2018 | 0.1211 | 0.1554 | 1.6418 | 0.0000 | 0.1338 | 0.1933 | 0.0113 | 8 | 0.0019 | 13.8667 | 86.1333 | 0 | NA |
| `right_swing_40960` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0213 | 0.2666 | 0.1181 | 0.1506 | 1.6323 | 0.0000 | 0.9479 | 0.1870 | 0.0113 | 11 | 0.0029 | 14.9333 | 85.0667 | 0 | NA |
| `right_swing_40960` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0204 | 0.2555 | 0.1198 | 0.1462 | 1.6382 | 0.0000 | 0.2772 | 0.1957 | 0.0184 | 9 | 0.0132 | 12.5333 | 87.2000 | 0 | NA |
| `right_swing_40960` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0209 | 0.2616 | 0.1205 | 0.1530 | 1.6347 | 0.0000 | 0.2359 | 0.1921 | 0.0164 | 14 | 0.0081 | 16.0000 | 84.0000 | 0 | NA |
| `right_swing_40960` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0197 | 0.2468 | 0.1148 | 0.1565 | 1.6434 | 0.0000 | 0.1960 | 0.1909 | 0.0111 | 11 | 0.0081 | 16.1333 | 83.8667 | 0 | NA |
| `right_swing_81920` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0194 | 0.2428 | 0.1264 | 0.1519 | 1.6250 | 0.0000 | 0.3437 | 0.1946 | 0.0141 | 11 | 0.0117 | 14.1333 | 85.8667 | 0 | NA |
| `right_swing_81920` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0209 | 0.2609 | 0.1165 | 0.1563 | 1.6232 | 0.0000 | 0.5465 | 0.1916 | 0.0118 | 15 | 0.0048 | 17.2000 | 82.6667 | 0 | NA |
| `right_swing_81920` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0226 | 0.2819 | 0.1250 | 0.1511 | 1.6512 | 0.0000 | 0.9045 | 0.1908 | 0.0135 | 8 | 0.0051 | 17.0667 | 82.9333 | 0 | NA |
| `right_swing_81920` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0173 | 0.2166 | 0.1218 | 0.1554 | 1.6290 | 0.0000 | 0.2087 | 0.1887 | 0.0110 | 8 | 0.0036 | 14.2667 | 85.7333 | 0 | NA |
| `right_swing_81920` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0208 | 0.2600 | 0.1156 | 0.1506 | 1.6295 | 0.0000 | 0.6973 | 0.1882 | 0.0112 | 11 | 0.0032 | 14.6667 | 85.3333 | 0 | NA |
| `right_swing_81920` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0195 | 0.2434 | 0.1181 | 0.1462 | 1.6488 | 0.0000 | 0.5340 | 0.1964 | 0.0186 | 8 | 0.0093 | 12.0000 | 87.7333 | 0 | NA |
| `right_swing_81920` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0188 | 0.2352 | 0.1176 | 0.1530 | 1.6489 | 0.0000 | 0.8915 | 0.1915 | 0.0165 | 6 | 0.0139 | 13.6000 | 86.4000 | 0 | NA |
| `right_swing_81920` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0201 | 0.2507 | 0.1140 | 0.1565 | 1.6500 | 0.0000 | 0.1947 | 0.1910 | 0.0111 | 12 | 0.0084 | 16.5333 | 83.4667 | 0 | NA |
| `right_swing_122880` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0198 | 0.2471 | 0.1226 | 0.1519 | 1.6295 | 0.0000 | 0.4363 | 0.1947 | 0.0138 | 9 | 0.0096 | 14.8000 | 85.2000 | 0 | NA |
| `right_swing_122880` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0214 | 0.2681 | 0.1206 | 0.1563 | 1.6363 | 0.0000 | 0.2048 | 0.1891 | 0.0110 | 12 | 0.0025 | 16.4000 | 83.4667 | 0 | NA |
| `right_swing_122880` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0219 | 0.2735 | 0.1237 | 0.1511 | 1.6306 | 0.0000 | 0.0000 | 0.1911 | 0.0140 | 10 | 0.0049 | 15.4667 | 84.5333 | 0 | NA |
| `right_swing_122880` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0164 | 0.2044 | 0.1207 | 0.1555 | 1.6143 | 0.0000 | 0.2800 | 0.1885 | 0.0102 | 8 | 0.0029 | 13.0667 | 86.9333 | 0 | NA |
| `right_swing_122880` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0213 | 0.2668 | 0.1168 | 0.1506 | 1.6205 | 0.0000 | 0.5681 | 0.1884 | 0.0107 | 6 | 0.0024 | 14.2667 | 85.7333 | 0 | NA |
| `right_swing_122880` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0214 | 0.2671 | 0.1211 | 0.1462 | 1.6422 | 0.0000 | 0.1917 | 0.1926 | 0.0185 | 9 | 0.0079 | 13.8667 | 85.8667 | 0 | NA |
| `right_swing_122880` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0201 | 0.2509 | 0.1196 | 0.1530 | 1.6391 | 0.0000 | 0.0309 | 0.1925 | 0.0165 | 8 | 0.0133 | 14.0000 | 86.0000 | 0 | NA |
| `right_swing_122880` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0176 | 0.2204 | 0.1127 | 0.1565 | 1.6314 | 0.0000 | 0.5336 | 0.1886 | 0.0112 | 8 | 0.0087 | 13.4667 | 86.5333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `right_swing_40960` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2526 | 0.0202 | 0.1203 | 0.1526 | 0.0000 | 0.4066 | 0.0133 | 10.5000 | 0.0057 | 15.1667 | 84.7833 | 0.0000 | NA |
| `right_swing_81920` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2490 | 0.0199 | 0.1194 | 0.1526 | 0.0000 | 0.5401 | 0.0135 | 9.8750 | 0.0075 | 14.9333 | 85.0167 | 0.0000 | NA |
| `right_swing_122880` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2498 | 0.0200 | 0.1197 | 0.1526 | 0.0000 | 0.2807 | 0.0132 | 8.7500 | 0.0065 | 14.4167 | 85.5333 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
