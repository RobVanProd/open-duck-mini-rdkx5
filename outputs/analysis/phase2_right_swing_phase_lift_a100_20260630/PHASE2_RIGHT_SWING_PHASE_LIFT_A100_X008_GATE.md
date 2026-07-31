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
| `right_phase_lift_40960` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0191 | 0.2391 | 0.1235 | 0.1519 | 1.6462 | 0.0000 | 0.0182 | 0.1940 | 0.0137 | 8 | 0.0111 | 14.6667 | 85.3333 | 0 | NA |
| `right_phase_lift_40960` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0207 | 0.2589 | 0.1196 | 0.1563 | 1.6553 | 0.0000 | 0.1576 | 0.1907 | 0.0110 | 17 | 0.0024 | 16.8000 | 83.0667 | 0 | NA |
| `right_phase_lift_40960` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0227 | 0.2835 | 0.1256 | 0.1511 | 1.6538 | 0.0000 | 0.0516 | 0.1905 | 0.0134 | 9 | 0.0053 | 16.9333 | 83.0667 | 0 | NA |
| `right_phase_lift_40960` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0178 | 0.2220 | 0.1189 | 0.1554 | 1.6471 | 0.0000 | 0.1350 | 0.1889 | 0.0111 | 10 | 0.0015 | 13.4667 | 86.5333 | 0 | NA |
| `right_phase_lift_40960` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0211 | 0.2633 | 0.1179 | 0.1506 | 1.6408 | 0.0000 | 0.0000 | 0.1921 | 0.0112 | 6 | 0.0044 | 13.7333 | 86.2667 | 0 | NA |
| `right_phase_lift_40960` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0204 | 0.2547 | 0.1179 | 0.1462 | 1.6484 | 0.0000 | 0.3710 | 0.1954 | 0.0184 | 11 | 0.0114 | 13.4667 | 86.2667 | 0 | NA |
| `right_phase_lift_40960` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0210 | 0.2628 | 0.1178 | 0.1530 | 1.6456 | 0.0000 | 0.0588 | 0.1923 | 0.0166 | 11 | 0.0128 | 13.8667 | 86.1333 | 0 | NA |
| `right_phase_lift_40960` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0181 | 0.2267 | 0.1171 | 0.1565 | 1.6406 | 0.0000 | 0.0129 | 0.1903 | 0.0110 | 9 | 0.0088 | 13.8667 | 86.1333 | 0 | NA |
| `right_phase_lift_81920` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0174 | 0.2172 | 0.1205 | 0.1519 | 1.6263 | 0.0000 | 0.0000 | 0.1950 | 0.0137 | 8 | 0.0118 | 11.8667 | 88.1333 | 0 | NA |
| `right_phase_lift_81920` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0204 | 0.2547 | 0.1183 | 0.1563 | 1.6284 | 0.0000 | 0.0259 | 0.1911 | 0.0108 | 8 | 0.0031 | 16.1333 | 83.7333 | 0 | NA |
| `right_phase_lift_81920` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0224 | 0.2804 | 0.1229 | 0.1511 | 1.6479 | 0.0000 | 0.1843 | 0.1889 | 0.0133 | 6 | 0.0059 | 15.0667 | 84.9333 | 0 | NA |
| `right_phase_lift_81920` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0173 | 0.2167 | 0.1226 | 0.1554 | 1.6493 | 0.0000 | 0.4232 | 0.1902 | 0.0109 | 4 | 0.0007 | 14.5333 | 85.4667 | 0 | NA |
| `right_phase_lift_81920` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0223 | 0.2785 | 0.1200 | 0.1506 | 1.6169 | 0.0000 | 0.0000 | 0.1881 | 0.0120 | 8 | 0.0036 | 14.2667 | 85.7333 | 0 | NA |
| `right_phase_lift_81920` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0213 | 0.2658 | 0.1186 | 0.1462 | 1.6358 | 0.0000 | 0.0000 | 0.1920 | 0.0185 | 9 | 0.0109 | 13.0667 | 86.6667 | 0 | NA |
| `right_phase_lift_81920` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0202 | 0.2527 | 0.1139 | 0.1530 | 1.6403 | 0.0000 | 0.0000 | 0.1927 | 0.0165 | 13 | 0.0094 | 13.3333 | 86.6667 | 0 | NA |
| `right_phase_lift_81920` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0185 | 0.2311 | 0.1151 | 0.1565 | 1.6259 | 0.0000 | 0.0702 | 0.1893 | 0.0110 | 8 | 0.0091 | 13.4667 | 86.5333 | 0 | NA |
| `right_phase_lift_122880` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0212 | 0.2654 | 0.1236 | 0.1519 | 1.6327 | 0.0000 | 0.0000 | 0.1888 | 0.0139 | 8 | 0.0112 | 15.0667 | 84.9333 | 0 | NA |
| `right_phase_lift_122880` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0199 | 0.2493 | 0.1184 | 0.1563 | 1.6279 | 0.0000 | 0.3636 | 0.1904 | 0.0107 | 12 | 0.0017 | 16.0000 | 83.8667 | 0 | NA |
| `right_phase_lift_122880` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0231 | 0.2890 | 0.1220 | 0.1511 | 1.6638 | 0.0000 | 0.3254 | 0.1908 | 0.0136 | 10 | 0.0048 | 16.6667 | 83.3333 | 0 | NA |
| `right_phase_lift_122880` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0175 | 0.2183 | 0.1201 | 0.1554 | 1.6399 | 0.0000 | 0.0000 | 0.1876 | 0.0117 | 10 | 0.0022 | 13.4667 | 86.5333 | 0 | NA |
| `right_phase_lift_122880` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0217 | 0.2710 | 0.1142 | 0.1506 | 1.6279 | 0.0000 | 0.3222 | 0.1884 | 0.0111 | 10 | 0.0027 | 14.0000 | 86.0000 | 0 | NA |
| `right_phase_lift_122880` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0224 | 0.2795 | 0.1198 | 0.1462 | 1.6132 | 0.0000 | 0.0000 | 0.1893 | 0.0185 | 11 | 0.0070 | 14.4000 | 85.3333 | 0 | NA |
| `right_phase_lift_122880` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0213 | 0.2667 | 0.1204 | 0.1530 | 1.6404 | 0.0000 | 0.4707 | 0.1922 | 0.0165 | 10 | 0.0116 | 16.4000 | 83.6000 | 0 | NA |
| `right_phase_lift_122880` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0186 | 0.2328 | 0.1145 | 0.1565 | 1.6400 | 0.0000 | 0.0000 | 0.1907 | 0.0110 | 10 | 0.0083 | 15.0667 | 84.9333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `right_phase_lift_40960` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2514 | 0.0201 | 0.1198 | 0.1526 | 0.0000 | 0.1007 | 0.0133 | 10.1250 | 0.0072 | 14.6000 | 85.3500 | 0.0000 | NA |
| `right_phase_lift_81920` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2496 | 0.0200 | 0.1190 | 0.1526 | 0.0000 | 0.0879 | 0.0133 | 8.0000 | 0.0068 | 13.9667 | 85.9833 | 0.0000 | NA |
| `right_phase_lift_122880` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2590 | 0.0207 | 0.1191 | 0.1526 | 0.0000 | 0.1852 | 0.0134 | 10.1250 | 0.0062 | 15.1333 | 84.8167 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
