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
seeds: `[1, 2, 3, 4, 5, 6]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[1, 2, 3, 4, 5, 6]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter6_weight2_control_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 494 | `fall_or_nan` | -0.0086 | -0.1076 | 0.1686 | 0.0851 | 1.5869 | 0.0000 | 0.0000 | 0.1811 | 0.0349 | 10 | 0.0116 | 23.8866 | 75.7085 | 8 | 0.8750 |
| `iter6_weight2_control_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 157 | `fall_or_nan` | 0.1357 | 1.6957 | 0.8387 | 0.0005 | 1.5888 | 0.0000 | 0.0000 | 0.2079 | 0.0592 | 1 | 0.0061 | 21.6561 | 77.7070 | 2 | 0.5000 |
| `iter6_weight2_control_rate150` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 450 | `fall_or_nan` | -0.0219 | -0.2733 | 0.1462 | 0.0776 | 1.5873 | 0.0000 | 0.3926 | 0.1759 | 0.0335 | 7 | 0.0114 | 19.5556 | 79.7778 | 8 | 0.8750 |
| `iter6_weight2_control_rate150` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 724 | `fall_or_nan` | 0.0538 | 0.6728 | 0.2474 | 0.0018 | 1.5699 | 0.0000 | 0.0000 | 0.1886 | 0.0576 | 14 | 0.0060 | 23.0663 | 76.7956 | 12 | 0.9167 |
| `iter6_weight2_control_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -0.3117 | -3.8964 | 0.0513 | 0.0706 | 1.8811 | 0.0000 | 0.0000 | 0.2332 | 0.0304 | 1 | 0.0171 | 14.8936 | 74.4681 | 0 | NA |
| `iter6_weight2_control_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 246 | `fall_or_nan` | -0.0519 | -0.6486 | 0.1091 | 0.0687 | 1.5820 | 0.0000 | 0.0000 | 0.1786 | 0.0325 | 4 | 0.0167 | 21.1382 | 78.4553 | 4 | 0.7500 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter6_weight2_control_rate150` | 6 | 6 | 0 | 353.0000 | 47 | 724 | -0.4262 | -0.0341 | 0.2602 | 0.0507 | 0.0000 | 0.0654 | 0.0413 | 6.1667 | 0.0115 | 20.6994 | 77.1520 | 5.6667 | 0.7833 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
