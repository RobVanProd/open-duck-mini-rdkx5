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
| `right_phase_single_support_40960` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0194 | 0.2425 | 0.1235 | 0.1519 | 1.6562 | 0.0000 | 0.3138 | 0.1939 | 0.0134 | 7 | 0.0078 | 13.7333 | 86.2667 | 0 | NA |
| `right_phase_single_support_40960` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0199 | 0.2486 | 0.1176 | 0.1563 | 1.6442 | 0.0000 | 0.3488 | 0.1915 | 0.0108 | 9 | 0.0039 | 16.2667 | 83.6000 | 0 | NA |
| `right_phase_single_support_40960` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0225 | 0.2817 | 0.1248 | 0.1511 | 1.6608 | 0.0000 | 0.0000 | 0.1931 | 0.0131 | 9 | 0.0052 | 16.6667 | 83.3333 | 0 | NA |
| `right_phase_single_support_40960` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0175 | 0.2189 | 0.1248 | 0.1554 | 1.6341 | 0.0000 | 0.2583 | 0.1896 | 0.0116 | 8 | 0.0029 | 14.1333 | 85.8667 | 0 | NA |
| `right_phase_single_support_40960` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0208 | 0.2606 | 0.1132 | 0.1506 | 1.6444 | 0.0000 | 0.3770 | 0.1909 | 0.0105 | 11 | 0.0039 | 14.4000 | 85.6000 | 0 | NA |
| `right_phase_single_support_40960` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0203 | 0.2540 | 0.1211 | 0.1462 | 1.6476 | 0.0000 | 0.3090 | 0.1944 | 0.0185 | 9 | 0.0078 | 13.3333 | 86.4000 | 0 | NA |
| `right_phase_single_support_40960` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0201 | 0.2513 | 0.1189 | 0.1530 | 1.6471 | 0.0000 | 0.5379 | 0.1972 | 0.0165 | 11 | 0.0116 | 14.9333 | 85.0667 | 0 | NA |
| `right_phase_single_support_40960` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0181 | 0.2265 | 0.1150 | 0.1565 | 1.6466 | 0.0000 | 0.0000 | 0.1900 | 0.0110 | 10 | 0.0086 | 13.0667 | 86.9333 | 0 | NA |
| `right_phase_single_support_81920` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0205 | 0.2564 | 0.1211 | 0.1519 | 1.6416 | 0.0000 | 0.0000 | 0.1922 | 0.0134 | 10 | 0.0063 | 14.0000 | 86.0000 | 0 | NA |
| `right_phase_single_support_81920` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0211 | 0.2639 | 0.1187 | 0.1563 | 1.6309 | 0.0000 | 0.3085 | 0.1900 | 0.0112 | 16 | 0.0032 | 17.0667 | 82.8000 | 0 | NA |
| `right_phase_single_support_81920` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0217 | 0.2713 | 0.1208 | 0.1511 | 1.6529 | 0.0000 | 0.2868 | 0.1886 | 0.0132 | 9 | 0.0049 | 16.2667 | 83.7333 | 0 | NA |
| `right_phase_single_support_81920` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0175 | 0.2184 | 0.1222 | 0.1554 | 1.6332 | 0.0000 | 0.6026 | 0.1903 | 0.0110 | 6 | 0.0009 | 12.8000 | 87.2000 | 0 | NA |
| `right_phase_single_support_81920` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0206 | 0.2578 | 0.1162 | 0.1506 | 1.6148 | 0.0000 | 0.0000 | 0.1884 | 0.0112 | 9 | 0.0028 | 13.3333 | 86.6667 | 0 | NA |
| `right_phase_single_support_81920` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0206 | 0.2572 | 0.1231 | 0.1462 | 1.6387 | 0.0000 | 0.0000 | 0.1949 | 0.0185 | 10 | 0.0145 | 12.8000 | 86.9333 | 0 | NA |
| `right_phase_single_support_81920` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0208 | 0.2602 | 0.1167 | 0.1530 | 1.6237 | 0.0000 | 0.9484 | 0.1908 | 0.0165 | 9 | 0.0119 | 14.9333 | 85.0667 | 0 | NA |
| `right_phase_single_support_81920` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0192 | 0.2404 | 0.1100 | 0.1565 | 1.6547 | 0.0000 | 0.0115 | 0.1890 | 0.0110 | 13 | 0.0079 | 14.1333 | 85.8667 | 0 | NA |
| `right_phase_single_support_122880` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0187 | 0.2343 | 0.1196 | 0.1519 | 1.6199 | 0.0000 | 0.0000 | 0.1902 | 0.0140 | 7 | 0.0097 | 13.4667 | 86.5333 | 0 | NA |
| `right_phase_single_support_122880` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0207 | 0.2590 | 0.1198 | 0.1563 | 1.6452 | 0.0000 | 0.4701 | 0.1885 | 0.0110 | 14 | 0.0020 | 17.0667 | 82.8000 | 0 | NA |
| `right_phase_single_support_122880` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0224 | 0.2804 | 0.1232 | 0.1511 | 1.6493 | 0.0000 | 0.2985 | 0.1915 | 0.0124 | 11 | 0.0054 | 16.6667 | 83.3333 | 0 | NA |
| `right_phase_single_support_122880` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0194 | 0.2428 | 0.1229 | 0.1554 | 1.6311 | 0.0000 | 0.0000 | 0.1886 | 0.0109 | 6 | 0.0045 | 15.7333 | 84.2667 | 0 | NA |
| `right_phase_single_support_122880` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0217 | 0.2710 | 0.1173 | 0.1506 | 1.6172 | 0.0000 | 0.3278 | 0.1867 | 0.0107 | 8 | 0.0036 | 13.6000 | 86.4000 | 0 | NA |
| `right_phase_single_support_122880` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0206 | 0.2573 | 0.1209 | 0.1462 | 1.6345 | 0.0000 | 0.1709 | 0.1941 | 0.0184 | 7 | 0.0146 | 12.4000 | 87.3333 | 0 | NA |
| `right_phase_single_support_122880` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0214 | 0.2676 | 0.1142 | 0.1530 | 1.6424 | 0.0000 | 0.0374 | 0.1853 | 0.0164 | 7 | 0.0136 | 16.2667 | 83.7333 | 0 | NA |
| `right_phase_single_support_122880` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0185 | 0.2308 | 0.1136 | 0.1565 | 1.6147 | 0.0000 | 0.3320 | 0.1893 | 0.0112 | 10 | 0.0088 | 14.1333 | 85.8667 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `right_phase_single_support_40960` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2480 | 0.0198 | 0.1199 | 0.1526 | 0.0000 | 0.2681 | 0.0132 | 9.2500 | 0.0065 | 14.5667 | 85.3833 | 0.0000 | NA |
| `right_phase_single_support_81920` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2532 | 0.0203 | 0.1186 | 0.1526 | 0.0000 | 0.2697 | 0.0132 | 10.2500 | 0.0066 | 14.4167 | 85.5333 | 0.0000 | NA |
| `right_phase_single_support_122880` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2554 | 0.0204 | 0.1189 | 0.1526 | 0.0000 | 0.2046 | 0.0131 | 8.7500 | 0.0078 | 14.9167 | 85.0333 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
