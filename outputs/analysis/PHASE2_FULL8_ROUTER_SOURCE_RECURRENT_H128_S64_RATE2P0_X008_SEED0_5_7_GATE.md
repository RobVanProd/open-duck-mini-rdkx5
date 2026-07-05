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
| `recurrent_h128_s64_rate2p0` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 63 | `fall_or_nan` | -0.2476 | -3.0944 | 0.0417 | 0.0761 | 5.2400 | 3.2400 | 3.2400 | 0.2709 | 0.0388 | 2 | 0.0403 | 36.5079 | 60.3175 | 1 | 0.0000 |
| `recurrent_h128_s64_rate2p0` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 63 | `fall_or_nan` | -0.2461 | -3.0761 | 0.0417 | 0.0780 | 5.2400 | 3.2400 | 3.2400 | 0.2726 | 0.0379 | 2 | 0.0321 | 38.0952 | 60.3175 | 1 | 0.0000 |
| `recurrent_h128_s64_rate2p0` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 63 | `fall_or_nan` | -0.2467 | -3.0841 | 0.0417 | 0.0767 | 5.2400 | 3.2400 | 3.2400 | 0.2709 | 0.0381 | 2 | 0.0400 | 36.5079 | 60.3175 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_h128_s64_rate2p0` | 3 | 3 | 0 | 63.0000 | 63 | 63 | -3.0849 | -0.2468 | 0.0417 | 0.0769 | 3.2400 | 3.2400 | 0.0383 | 2.0000 | 0.0375 | 37.0370 | 60.3175 | 0.6667 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
