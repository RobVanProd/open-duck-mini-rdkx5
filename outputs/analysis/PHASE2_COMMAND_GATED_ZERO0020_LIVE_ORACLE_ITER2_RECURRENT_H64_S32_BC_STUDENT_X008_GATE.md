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
seeds: `[0, 1, 2, 6, 7]`
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
trace_seeds: `[0, 1, 2, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.3346 | -4.1824 | 0.0542 | 0.0682 | 5.2400 | 3.2400 | 3.2400 | 0.2746 | 0.0389 | 2 | 0.0179 | 26.3158 | 64.9123 | 0 | NA |
| `recurrent` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.3346 | -4.1820 | 0.0542 | 0.0683 | 5.2400 | 3.2400 | 3.2400 | 0.2746 | 0.0362 | 2 | 0.0093 | 29.8246 | 64.9123 | 1 | 0.0000 |
| `recurrent` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.3346 | -4.1820 | 0.0542 | 0.0682 | 5.2400 | 3.2400 | 3.2400 | 0.2746 | 0.0390 | 2 | 0.0180 | 26.3158 | 64.9123 | 1 | 0.0000 |
| `recurrent` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.3344 | -4.1794 | 0.0542 | 0.0682 | 5.2400 | 3.2400 | 3.2400 | 0.2746 | 0.0390 | 2 | 0.0176 | 26.3158 | 64.9123 | 1 | 0.0000 |
| `recurrent` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.3346 | -4.1824 | 0.0542 | 0.0682 | 5.2400 | 3.2400 | 3.2400 | 0.2746 | 0.0389 | 2 | 0.0179 | 26.3158 | 64.9123 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent` | 5 | 5 | 0 | 57.0000 | 57 | 57 | -4.1817 | -0.3345 | 0.0542 | 0.0682 | 3.2400 | 3.2400 | 0.0384 | 2.0000 | 0.0161 | 27.0175 | 64.9123 | 0.6000 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
