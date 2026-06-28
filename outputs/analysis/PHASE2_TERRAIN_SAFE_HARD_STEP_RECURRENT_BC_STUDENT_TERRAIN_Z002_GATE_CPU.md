# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[2, 4]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[2, 4]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_terrain_bc` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 84 | `fall_or_nan` | -0.1820 | -2.2744 | 0.0103 | 0.0559 | 5.2400 | 3.2400 | 0.2478 | 0.0346 | 4 | 0.0206 | 51.1905 | 47.6190 | 0 | NA |
| `recurrent_terrain_bc` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 46 | `fall_or_nan` | -0.3372 | -4.2154 | 0.0181 | 0.0542 | 5.2400 | 3.2400 | 0.2975 | 0.0356 | 3 | 0.0119 | 47.8261 | 45.6522 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_terrain_bc` | 2 | 2 | 0 | 65.0000 | 46 | 84 | -3.2449 | -0.2596 | 0.0142 | 0.0551 | 3.2400 | 0.0351 | 3.5000 | 0.0162 | 49.5083 | 46.6356 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
