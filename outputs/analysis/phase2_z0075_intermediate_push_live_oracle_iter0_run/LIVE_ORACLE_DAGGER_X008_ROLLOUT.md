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
| `student` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0265 | 0.3313 | 0.1602 | 0.1527 | 1.5437 | 0.0000 | 3.2400 | 0.1901 | 0.0180 | 14 | 0.0177 | 22.8000 | 77.2000 | 12 | 0.9167 |
| `student` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 582 | `fall_or_nan` | 0.0598 | 0.7473 | 0.2914 | -0.0052 | 1.5722 | 0.0000 | 3.2400 | 0.1937 | 0.0593 | 12 | 0.0121 | 26.1168 | 73.7113 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 2 | 1 | 1 | 666.0000 | 582 | 750 | 0.5393 | 0.0431 | 0.2258 | 0.0737 | 0.0000 | 3.2400 | 0.0387 | 13.0000 | 0.0149 | 24.4584 | 75.4557 | 10.0000 | 0.8958 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
