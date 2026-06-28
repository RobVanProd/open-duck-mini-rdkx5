# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[4, 5, 6]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[4, 5, 6]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_capped` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0036 | NA | 0.0685 | 0.1507 | 0.9632 | 0.0000 | 0.0888 | 0.0079 | 0 | 0.0000 | 0.4000 | 99.6000 | 0 | NA |
| `seed5_capped` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 42 | `fall_or_nan` | -0.3675 | NA | 0.0644 | 0.0509 | 2.0201 | 0.0000 | 0.2289 | 0.0311 | 2 | 0.0075 | 9.5238 | 78.5714 | 0 | NA |
| `seed5_capped` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0009 | NA | 0.0411 | 0.1532 | 1.1851 | 0.0000 | 0.1029 | 0.0224 | 1 | 0.0165 | 5.2000 | 94.8000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_capped` | 3 | 1 | 2 | 180.6667 | 42 | 250 | NA | -0.1210 | 0.0580 | 0.1183 | 0.0000 | 0.0205 | 1.0000 | 0.0080 | 5.0413 | 90.9905 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
