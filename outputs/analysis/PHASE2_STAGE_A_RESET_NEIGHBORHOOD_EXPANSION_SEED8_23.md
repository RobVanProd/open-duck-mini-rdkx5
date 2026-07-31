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
seeds: `[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]`
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
trace_seeds: `[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_expansion` | 8 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0565 | 0.7061 | 0.1036 | 0.1475 | 1.8409 | 0.0000 | 0.0000 | 0.2991 | 0.0082 | 1 | 0.0003 | 10.0000 | 88.0000 | 0 | NA |
| `baseline_expansion` | 9 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.4078 | -5.0975 | 0.0626 | 0.0595 | 1.7815 | 0.0000 | 0.0000 | 0.2659 | 0.0232 | 0 | 0.0000 | 38.2353 | 58.8235 | 0 | NA |
| `baseline_expansion` | 10 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0599 | 0.7484 | 0.0920 | 0.1507 | 1.7155 | 0.0000 | 0.0000 | 0.1991 | 0.0071 | 0 | 0.0000 | 14.0000 | 86.0000 | 0 | NA |
| `baseline_expansion` | 11 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0317 | 0.3963 | 0.1510 | 0.1560 | 1.6591 | 0.0000 | 0.0000 | 0.2426 | 0.0107 | 3 | 0.0072 | 50.0000 | 50.0000 | 0 | NA |
| `baseline_expansion` | 12 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 37 | `fall_or_nan` | -0.3838 | -4.7970 | 0.0481 | 0.0641 | 1.6953 | 0.0000 | 0.0000 | 0.2337 | 0.0248 | 2 | 0.0070 | 48.6486 | 48.6486 | 0 | NA |
| `baseline_expansion` | 13 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0825 | -1.0314 | 0.2058 | 0.1561 | 1.6523 | 0.0000 | 0.0000 | 0.1830 | 0.0079 | 0 | 0.0000 | 36.0000 | 64.0000 | 0 | NA |
| `baseline_expansion` | 14 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 41 | `fall_or_nan` | -0.0666 | -0.8322 | 0.1747 | 0.0885 | 1.5639 | 0.0000 | 0.0000 | 0.3747 | 0.0145 | 1 | 0.0217 | 92.6829 | 0.0000 | 0 | NA |
| `baseline_expansion` | 15 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0067 | -0.0843 | 0.0720 | 0.1577 | 1.4795 | 0.0000 | 0.0000 | 0.1996 | 0.0051 | 2 | 0.0044 | 64.0000 | 32.0000 | 0 | NA |
| `baseline_expansion` | 16 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0696 | -0.8704 | 0.2608 | 0.1544 | 1.5824 | 0.0000 | 0.0000 | 0.1682 | -0.0022 | 0 | 0.0000 | 8.0000 | 92.0000 | 0 | NA |
| `baseline_expansion` | 17 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0170 | 0.2126 | 0.0609 | 0.1527 | 1.7248 | 0.0000 | 0.0000 | 0.1699 | 0.0050 | 0 | 0.0000 | 6.0000 | 94.0000 | 0 | NA |
| `baseline_expansion` | 18 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0552 | 0.6896 | 0.0874 | 0.1516 | 1.6774 | 0.0000 | 0.0000 | 0.2341 | 0.0082 | 1 | 0.0004 | 12.0000 | 88.0000 | 0 | NA |
| `baseline_expansion` | 19 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | -0.0801 | -1.0011 | 0.1615 | 0.0691 | 1.9335 | 0.0000 | 0.0000 | 0.6040 | 0.0349 | 1 | 0.0342 | 65.6250 | 9.3750 | 0 | NA |
| `baseline_expansion` | 20 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 27 | `fall_or_nan` | 0.0297 | 0.3716 | 0.3761 | 0.0985 | 1.3441 | 0.0000 | 0.0000 | 0.4243 | 0.0062 | 1 | 0.0340 | 81.4815 | 0.0000 | 0 | NA |
| `baseline_expansion` | 21 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0147 | 0.1837 | 0.0826 | 0.1517 | 1.7520 | 0.0000 | 0.0000 | 0.2098 | 0.0042 | 0 | 0.0000 | 10.0000 | 90.0000 | 0 | NA |
| `baseline_expansion` | 22 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0398 | 0.4981 | 0.0888 | 0.1527 | 1.7216 | 0.0000 | 0.0000 | 0.2771 | 0.0069 | 0 | 0.0000 | 6.0000 | 94.0000 | 0 | NA |
| `baseline_expansion` | 23 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0067 | -0.0841 | 0.1445 | 0.1554 | 1.5845 | 0.0000 | 0.0000 | 0.1648 | 0.0015 | 0 | 0.0000 | 12.0000 | 88.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_expansion` | 16 | 5 | 11 | 45.0625 | 27 | 50 | -0.6245 | -0.0500 | 0.1358 | 0.1291 | 0.0000 | 0.0000 | 0.0104 | 0.7500 | 0.0068 | 34.6671 | 61.4279 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
