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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter17_motion_recurrent` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 311 | `fall_or_nan` | -0.0345 | -0.4313 | 0.1984 | 0.0763 | 1.7330 | 0.0000 | 2.8166 | 0.1858 | 0.0338 | 6 | 0.0154 | 20.5788 | 78.7781 | 5 | 0.6000 |
| `iter17_motion_recurrent` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 692 | `fall_or_nan` | 0.0531 | 0.6636 | 0.2805 | -0.0049 | 1.6665 | 0.0000 | 0.1971 | 0.1919 | 0.0576 | 17 | 0.0191 | 23.9884 | 75.7225 | 12 | 0.8333 |
| `iter17_motion_recurrent` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0307 | 0.3838 | 0.1744 | 0.1532 | 1.6755 | 0.0000 | 0.1971 | 0.1876 | 0.0138 | 15 | 0.0210 | 27.0667 | 72.9333 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter17_motion_recurrent` | 3 | 2 | 1 | 584.3333 | 311 | 750 | 0.2054 | 0.0164 | 0.2178 | 0.0749 | 0.0000 | 1.0703 | 0.0351 | 12.6667 | 0.0185 | 23.8780 | 75.8113 | 10.0000 | 0.7855 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
