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
seeds: `[0, 7]`
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
trace_seeds: `[0, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter5_antilunge_zero50_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 205 | `fall_or_nan` | 0.1184 | 1.4794 | 0.7268 | -0.0018 | 1.5909 | 0.0000 | 0.0000 | 0.2001 | 0.0576 | 4 | 0.0206 | 22.4390 | 76.5854 | 3 | 0.6667 |
| `iter5_antilunge_zero50_rate150` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 621 | `fall_or_nan` | 0.0559 | 0.6987 | 0.2770 | -0.0034 | 1.5772 | 0.0000 | 2.7400 | 0.1881 | 0.0591 | 14 | 0.0207 | 24.6377 | 74.8792 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter5_antilunge_zero50_rate150` | 2 | 2 | 0 | 413.0000 | 205 | 621 | 1.0891 | 0.0871 | 0.5019 | -0.0026 | 0.0000 | 1.3700 | 0.0584 | 9.0000 | 0.0206 | 23.5384 | 75.7323 | 5.5000 | 0.7708 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
