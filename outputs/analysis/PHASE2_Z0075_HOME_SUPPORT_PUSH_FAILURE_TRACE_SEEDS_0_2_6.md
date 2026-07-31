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
seeds: `[0, 2, 6]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 2, 6]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter10_spike_local_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 114 | `fall_or_nan` | 0.1756 | 2.1946 | 0.9954 | 0.0059 | 1.5890 | 0.0000 | 0.0000 | 0.1950 | 0.0524 | 2 | 0.0053 | 14.0351 | 85.0877 | 1 | 0.0000 |
| `iter10_spike_local_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 604 | `fall_or_nan` | -0.0023 | -0.0289 | 0.1749 | 0.0821 | 1.5685 | 0.0000 | 0.0000 | 0.1756 | 0.0363 | 14 | 0.0132 | 25.6623 | 74.0066 | 10 | 0.9000 |
| `iter10_spike_local_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 672 | `fall_or_nan` | 0.0009 | 0.0114 | 0.1562 | 0.0755 | 1.5578 | 0.0000 | 0.0000 | 0.1764 | 0.0366 | 10 | 0.0129 | 25.0000 | 74.8512 | 12 | 0.8333 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter10_spike_local_rate150` | 3 | 3 | 0 | 463.3333 | 114 | 672 | 0.7257 | 0.0581 | 0.4422 | 0.0545 | 0.0000 | 0.0000 | 0.0418 | 8.6667 | 0.0105 | 21.5658 | 77.9818 | 7.6667 | 0.5778 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
