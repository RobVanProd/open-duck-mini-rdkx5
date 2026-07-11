# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `1.0`
seeds: `[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `None`
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `independent_baseline` | 40 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0105 | -0.1307 | 0.1027 | 0.1580 | 1.5291 | 0.0000 | 0.0000 | 0.2058 | 0.0080 | 1 | 0.0063 | 18.0000 | 78.0000 | 0 | NA |
| `independent_baseline` | 41 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 38 | `fall_or_nan` | -0.0995 | -1.2433 | 0.2808 | 0.0563 | 1.5331 | 0.0000 | 0.0000 | 0.2167 | 0.0253 | 1 | 0.0202 | 89.4737 | 0.0000 | 0 | NA |
| `independent_baseline` | 42 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | -0.0581 | -0.7258 | 0.1471 | 0.0608 | 1.5362 | 0.0000 | 0.0000 | 0.3392 | 0.0192 | 1 | 0.0057 | 88.5714 | 0.0000 | 0 | NA |
| `independent_baseline` | 43 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 43 | `fall_or_nan` | -0.0711 | -0.8889 | 0.2485 | 0.0637 | 1.5441 | 0.0000 | 0.0000 | 0.3126 | 0.0110 | 1 | 0.0261 | 95.3488 | 0.0000 | 0 | NA |
| `independent_baseline` | 44 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 29 | `fall_or_nan` | -0.4448 | -5.5600 | 0.0391 | 0.0759 | 1.7388 | 0.0000 | 0.0000 | 0.3280 | 0.0216 | 1 | 0.0141 | 34.4828 | 55.1724 | 0 | NA |
| `independent_baseline` | 45 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0083 | -0.1032 | 0.0768 | 0.1554 | 1.6210 | 0.0000 | 0.0000 | 0.2178 | 0.0007 | 0 | 0.0000 | 10.0000 | 90.0000 | 0 | NA |
| `independent_baseline` | 46 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0443 | 0.5543 | 0.1046 | 0.1509 | 1.7094 | 0.0000 | 0.0000 | 0.2272 | 0.0075 | 1 | 0.0016 | 24.0000 | 76.0000 | 0 | NA |
| `independent_baseline` | 47 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0007 | 0.0082 | 0.0495 | 0.1562 | 1.5378 | 0.0000 | 0.0000 | 0.2411 | 0.0024 | 0 | 0.0000 | 18.0000 | 80.0000 | 0 | NA |
| `independent_baseline` | 48 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.0685 | -0.8557 | 0.0831 | 0.0885 | 1.4427 | 0.0000 | 0.0000 | 0.3742 | 0.0170 | 1 | 0.0085 | 81.2500 | 6.2500 | 0 | NA |
| `independent_baseline` | 49 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3341 | -4.1757 | 0.0003 | 0.0689 | 1.8779 | 0.0000 | 0.0000 | 0.2565 | 0.0273 | 2 | 0.0103 | 29.1667 | 64.5833 | 0 | NA |
| `independent_baseline` | 50 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0602 | -0.7525 | 0.2941 | 0.1405 | 1.6321 | 0.0000 | 0.0883 | 0.4115 | 0.0364 | 1 | 0.0071 | 98.0000 | 0.0000 | 0 | NA |
| `independent_baseline` | 51 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 36 | `fall_or_nan` | 0.4718 | 5.8977 | 1.4204 | 0.0024 | 1.4066 | 0.0000 | 0.0000 | 0.3857 | 0.0274 | 3 | 0.0061 | 69.4444 | 13.8889 | 0 | NA |
| `independent_baseline` | 52 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0567 | 0.7085 | 0.1035 | 0.1506 | 1.6927 | 0.0000 | 0.0000 | 0.2286 | 0.0103 | 1 | 0.0029 | 18.0000 | 82.0000 | 0 | NA |
| `independent_baseline` | 53 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0259 | 0.3239 | 0.1009 | 0.1516 | 1.6905 | 0.0000 | 0.0000 | 0.1675 | 0.0039 | 0 | 0.0000 | 12.0000 | 88.0000 | 0 | NA |
| `independent_baseline` | 54 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0572 | 0.7152 | 0.0960 | 0.1456 | 1.6858 | 0.0000 | 0.0000 | 0.2502 | 0.0145 | 0 | 0.0000 | 6.0000 | 92.0000 | 0 | NA |
| `independent_baseline` | 55 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0247 | 0.3083 | 0.0946 | 0.1517 | 1.6588 | 0.0000 | 0.0000 | 0.1655 | 0.0067 | 1 | 0.0010 | 12.0000 | 88.0000 | 0 | NA |
| `independent_baseline` | 56 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0575 | -0.7182 | 0.1887 | 0.1605 | 1.3850 | 0.0000 | 0.0000 | 0.2630 | 0.0220 | 1 | 0.0134 | 40.0000 | 50.0000 | 0 | NA |
| `independent_baseline` | 57 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 36 | `fall_or_nan` | -0.0426 | -0.5328 | 0.0461 | 0.0617 | 1.5894 | 0.0000 | 0.0000 | 0.3502 | 0.0168 | 1 | 0.0297 | 83.3333 | 0.0000 | 0 | NA |
| `independent_baseline` | 58 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.0169 | -0.2115 | 0.1051 | 0.0775 | 1.7146 | 0.0000 | 0.1419 | 0.5067 | 0.0126 | 1 | 0.0043 | 85.2941 | 5.8824 | 0 | NA |
| `independent_baseline` | 59 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0189 | 0.2366 | 0.1131 | 0.1534 | 1.7307 | 0.0000 | 0.0000 | 0.1997 | 0.0129 | 2 | 0.0144 | 42.0000 | 58.0000 | 0 | NA |
| `independent_baseline` | 60 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0153 | 0.1909 | 0.0196 | 0.1563 | 1.5254 | 0.0000 | 0.0000 | 0.1933 | 0.0021 | 0 | 0.0000 | 2.0000 | 96.0000 | 0 | NA |
| `independent_baseline` | 61 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0064 | 0.0801 | 0.0457 | 0.1558 | 1.5570 | 0.0000 | 0.0000 | 0.1735 | 0.0059 | 1 | 0.0102 | 18.0000 | 78.0000 | 0 | NA |
| `independent_baseline` | 62 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0149 | 0.1865 | 0.0879 | 0.1518 | 1.6782 | 0.0000 | 0.0000 | 0.1739 | 0.0077 | 0 | 0.0000 | 10.0000 | 90.0000 | 0 | NA |
| `independent_baseline` | 63 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | -0.0617 | -0.7714 | 0.1281 | 0.0823 | 1.4383 | 0.0000 | 0.0000 | 0.3586 | 0.0190 | 1 | 0.0318 | 68.7500 | 6.2500 | 0 | NA |
| `independent_baseline` | 64 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0529 | 0.6614 | 0.0977 | 0.1510 | 1.6866 | 0.0000 | 0.0000 | 0.1970 | 0.0086 | 0 | 0.0000 | 12.0000 | 88.0000 | 0 | NA |
| `independent_baseline` | 65 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0060 | -0.0754 | 0.2542 | 0.1579 | 1.5238 | 0.0000 | 0.0000 | 0.3216 | 0.0277 | 2 | 0.0220 | 68.0000 | 22.0000 | 0 | NA |
| `independent_baseline` | 66 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.2659 | -3.3241 | 0.0682 | 0.0892 | 1.8009 | 0.0000 | 0.0000 | 0.2312 | 0.0271 | 0 | 0.0000 | 14.0000 | 82.0000 | 0 | NA |
| `independent_baseline` | 67 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0312 | 0.3897 | 0.0671 | 0.1536 | 1.6545 | 0.0000 | 0.0000 | 0.1637 | 0.0049 | 0 | 0.0000 | 8.0000 | 92.0000 | 0 | NA |
| `independent_baseline` | 68 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0084 | 0.1048 | 0.1891 | 0.1572 | 1.5183 | 0.0000 | 0.0000 | 0.2422 | 0.0006 | 1 | 0.0029 | 58.0000 | 42.0000 | 0 | NA |
| `independent_baseline` | 69 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0443 | -0.5542 | 0.1749 | 0.1546 | 0.9848 | 0.0000 | 0.0000 | 0.1155 | 0.0157 | 0 | 0.0000 | 8.0000 | 92.0000 | 0 | NA |
| `independent_baseline` | 70 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0346 | -0.4319 | 0.1385 | 0.1569 | 1.4037 | 0.0000 | 0.0000 | 0.2860 | 0.0260 | 1 | 0.0331 | 82.0000 | 16.0000 | 0 | NA |
| `independent_baseline` | 71 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 37 | `fall_or_nan` | -0.0579 | -0.7243 | 0.3700 | 0.1076 | 1.6598 | 0.0000 | 0.0000 | 0.4803 | 0.0058 | 1 | 0.0128 | 86.4865 | 5.4054 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `independent_baseline` | 32 | 11 | 21 | 45.8125 | 29 | 50 | -0.3567 | -0.0285 | 0.1667 | 0.1220 | 0.0000 | 0.0072 | 0.0142 | 0.8438 | 0.0089 | 43.4251 | 51.1698 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
