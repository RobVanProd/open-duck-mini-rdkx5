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
| `right_phase_advance_40960` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0199 | 0.2486 | 0.1222 | 0.1519 | 1.6407 | 0.0000 | 0.3012 | 0.1910 | 0.0136 | 8 | 0.0040 | 13.6000 | 86.4000 | 0 | NA |
| `right_phase_advance_40960` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0209 | 0.2614 | 0.1203 | 0.1563 | 1.6556 | 0.0000 | 0.6649 | 0.1915 | 0.0110 | 13 | 0.0017 | 18.2667 | 81.6000 | 0 | NA |
| `right_phase_advance_40960` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0220 | 0.2754 | 0.1248 | 0.1511 | 1.6591 | 0.0000 | 0.2818 | 0.1902 | 0.0136 | 11 | 0.0047 | 16.6667 | 83.3333 | 0 | NA |
| `right_phase_advance_40960` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0172 | 0.2154 | 0.1224 | 0.1554 | 1.6376 | 0.0000 | 0.0000 | 0.1890 | 0.0105 | 9 | 0.0048 | 13.6000 | 86.4000 | 0 | NA |
| `right_phase_advance_40960` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0211 | 0.2642 | 0.1191 | 0.1506 | 1.6190 | 0.0000 | 0.2614 | 0.1895 | 0.0123 | 10 | 0.0022 | 14.4000 | 85.6000 | 0 | NA |
| `right_phase_advance_40960` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0202 | 0.2525 | 0.1189 | 0.1462 | 1.6594 | 0.0000 | 0.0362 | 0.1960 | 0.0184 | 9 | 0.0064 | 12.2667 | 87.4667 | 0 | NA |
| `right_phase_advance_40960` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0192 | 0.2394 | 0.1140 | 0.1530 | 1.6339 | 0.0000 | 0.0006 | 0.1905 | 0.0166 | 11 | 0.0113 | 13.8667 | 86.1333 | 0 | NA |
| `right_phase_advance_40960` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0191 | 0.2382 | 0.1136 | 0.1565 | 1.6416 | 0.0000 | 0.4008 | 0.1905 | 0.0111 | 6 | 0.0108 | 14.4000 | 85.6000 | 0 | NA |
| `right_phase_advance_81920` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0197 | 0.2468 | 0.1235 | 0.1519 | 1.6404 | 0.0000 | 0.0866 | 0.1930 | 0.0137 | 12 | 0.0080 | 15.6000 | 84.4000 | 0 | NA |
| `right_phase_advance_81920` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0202 | 0.2526 | 0.1175 | 0.1563 | 1.6474 | 0.0000 | 0.0000 | 0.1911 | 0.0109 | 11 | 0.0024 | 16.1333 | 83.7333 | 0 | NA |
| `right_phase_advance_81920` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0224 | 0.2806 | 0.1244 | 0.1511 | 1.6440 | 0.0000 | 0.0000 | 0.1918 | 0.0126 | 8 | 0.0052 | 16.0000 | 84.0000 | 0 | NA |
| `right_phase_advance_81920` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0167 | 0.2088 | 0.1204 | 0.1554 | 1.6356 | 0.0000 | 0.2639 | 0.1872 | 0.0106 | 5 | 0.0019 | 12.1333 | 87.8667 | 0 | NA |
| `right_phase_advance_81920` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0211 | 0.2639 | 0.1175 | 0.1506 | 1.6271 | 0.0000 | 0.2392 | 0.1889 | 0.0111 | 9 | 0.0031 | 14.0000 | 86.0000 | 0 | NA |
| `right_phase_advance_81920` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0203 | 0.2537 | 0.1214 | 0.1462 | 1.6422 | 0.0000 | 0.0000 | 0.1927 | 0.0184 | 10 | 0.0120 | 13.0667 | 86.6667 | 0 | NA |
| `right_phase_advance_81920` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0210 | 0.2626 | 0.1177 | 0.1530 | 1.6306 | 0.0000 | 0.3148 | 0.1938 | 0.0165 | 14 | 0.0075 | 16.0000 | 84.0000 | 0 | NA |
| `right_phase_advance_81920` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0197 | 0.2462 | 0.1134 | 0.1565 | 1.6553 | 0.0000 | 0.0000 | 0.1921 | 0.0109 | 7 | 0.0100 | 14.9333 | 85.0667 | 0 | NA |
| `right_phase_advance_122880` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0201 | 0.2518 | 0.1233 | 0.1519 | 1.6312 | 0.0000 | 0.0212 | 0.1922 | 0.0138 | 11 | 0.0054 | 15.3333 | 84.6667 | 0 | NA |
| `right_phase_advance_122880` | 1 | `HOLD_CANDIDATE_TERRAIN_SWING` | 750 | `duration_complete` | 0.0207 | 0.2587 | 0.1222 | 0.1563 | 1.6225 | 0.0000 | 0.0000 | 0.1884 | 0.0114 | 14 | 0.0020 | 15.7333 | 84.1333 | 0 | NA |
| `right_phase_advance_122880` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0227 | 0.2837 | 0.1224 | 0.1511 | 1.6407 | 0.0000 | 0.0000 | 0.1907 | 0.0129 | 9 | 0.0059 | 16.4000 | 83.6000 | 0 | NA |
| `right_phase_advance_122880` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0157 | 0.1963 | 0.1211 | 0.1554 | 1.6356 | 0.0000 | 0.3312 | 0.1881 | 0.0108 | 11 | 0.0031 | 13.7333 | 86.2667 | 0 | NA |
| `right_phase_advance_122880` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0216 | 0.2703 | 0.1190 | 0.1506 | 1.6178 | 0.0000 | 0.0000 | 0.1873 | 0.0112 | 8 | 0.0068 | 13.0667 | 86.9333 | 0 | NA |
| `right_phase_advance_122880` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0200 | 0.2502 | 0.1225 | 0.1462 | 1.6414 | 0.0000 | 0.0000 | 0.1962 | 0.0184 | 8 | 0.0126 | 12.0000 | 87.7333 | 0 | NA |
| `right_phase_advance_122880` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0199 | 0.2492 | 0.1167 | 0.1530 | 1.6374 | 0.0000 | 0.3367 | 0.1924 | 0.0164 | 12 | 0.0096 | 14.5333 | 85.4667 | 0 | NA |
| `right_phase_advance_122880` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0198 | 0.2480 | 0.1122 | 0.1565 | 1.6524 | 0.0000 | 0.0000 | 0.1877 | 0.0111 | 8 | 0.0094 | 15.3333 | 84.6667 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `right_phase_advance_40960` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2494 | 0.0200 | 0.1194 | 0.1526 | 0.0000 | 0.2434 | 0.0134 | 9.6250 | 0.0057 | 14.6333 | 85.3167 | 0.0000 | NA |
| `right_phase_advance_81920` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2519 | 0.0202 | 0.1195 | 0.1526 | 0.0000 | 0.1131 | 0.0131 | 9.5000 | 0.0063 | 14.7333 | 85.2167 | 0.0000 | NA |
| `right_phase_advance_122880` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2510 | 0.0201 | 0.1199 | 0.1526 | 0.0000 | 0.0861 | 0.0133 | 10.1250 | 0.0069 | 14.5167 | 85.4333 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
