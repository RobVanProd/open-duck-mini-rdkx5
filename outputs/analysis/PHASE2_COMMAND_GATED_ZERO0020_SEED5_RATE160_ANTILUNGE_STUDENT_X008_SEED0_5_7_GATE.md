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
seeds: `[0, 5, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_antilunge_student` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 686 | `fall_or_nan` | -0.0008 | -0.0097 | 0.1809 | 0.0814 | 1.6777 | 0.0000 | 0.0000 | 0.1794 | 0.0328 | 11 | 0.0227 | 22.3032 | 77.5510 | 11 | 0.9091 |
| `seed5_antilunge_student` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 153 | `fall_or_nan` | 0.1327 | 1.6588 | 0.8227 | 0.0091 | 1.5969 | 0.0000 | 0.5781 | 0.1976 | 0.0602 | 0 | 0.0000 | 12.4183 | 86.9281 | 2 | 1.0000 |
| `seed5_antilunge_student` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 488 | `fall_or_nan` | 0.0617 | 0.7707 | 0.3638 | -0.0014 | 1.6440 | 0.0000 | 1.4007 | 0.1850 | 0.0602 | 12 | 0.0163 | 22.1311 | 77.2541 | 6 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_antilunge_student` | 3 | 3 | 0 | 442.3333 | 153 | 686 | 0.8066 | 0.0645 | 0.4558 | 0.0297 | 0.0000 | 0.6596 | 0.0511 | 7.6667 | 0.0130 | 18.9509 | 80.5777 | 6.3333 | 0.9697 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
