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
seeds: `[0, 2, 5]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
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
| `ppo_step0_seed5_equal_seed33` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0244 | 0.3052 | 0.1752 | 0.1583 | 1.5338 | 0.0000 | 0.0000 | 0.1791 | 0.0163 | 11 | 0.0259 | 21.7333 | 78.2667 | 12 | 0.9167 |
| `ppo_step0_seed5_equal_seed33` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0255 | 0.3191 | 0.1935 | 0.1563 | 1.5343 | 0.0000 | 0.0000 | 0.1841 | 0.0174 | 17 | 0.0190 | 24.6667 | 75.3333 | 13 | 0.9231 |
| `ppo_step0_seed5_equal_seed33` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 156 | `fall_or_nan` | 0.1332 | 1.6645 | 0.8113 | 0.0124 | 1.5372 | 0.0000 | 0.0000 | 0.1970 | 0.0614 | 2 | 0.0069 | 13.4615 | 85.2564 | 2 | 0.5000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0_seed5_equal_seed33` | 3 | 1 | 2 | 552.0000 | 156 | 750 | 0.7629 | 0.0610 | 0.3933 | 0.1090 | 0.0000 | 0.0000 | 0.0317 | 10.0000 | 0.0173 | 19.9538 | 79.6188 | 9.0000 | 0.7799 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
