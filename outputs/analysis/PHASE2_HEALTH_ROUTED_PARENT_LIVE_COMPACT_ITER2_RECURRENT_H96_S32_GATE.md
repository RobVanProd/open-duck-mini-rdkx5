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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_h96` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 92 | `fall_or_nan` | -0.1932 | -2.4153 | 0.0495 | 0.0568 | 5.2400 | 3.2400 | 3.2400 | 0.1530 | 0.0354 | 1 | 0.0082 | 1.0870 | 95.6522 | 1 | 0.0000 |
| `recurrent_h96` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 101 | `fall_or_nan` | -0.1653 | -2.0657 | 0.0486 | 0.0770 | 5.2400 | 3.2400 | 3.2400 | 0.1464 | 0.0347 | 0 | 0.0000 | 4.9505 | 95.0495 | 1 | 1.0000 |
| `recurrent_h96` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 94 | `fall_or_nan` | -0.1694 | -2.1178 | 0.0493 | 0.0872 | 5.2400 | 3.2400 | 3.2400 | 0.1549 | -0.0006 | 0 | 0.0000 | 7.4468 | 92.5532 | 1 | 1.0000 |
| `recurrent_h96` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 103 | `fall_or_nan` | -0.1600 | -2.0002 | 0.0483 | 0.0775 | 5.2400 | 3.2400 | 3.2400 | 0.1542 | 0.0347 | 1 | 0.0090 | 6.7961 | 91.2621 | 1 | 1.0000 |
| `recurrent_h96` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 96 | `fall_or_nan` | -0.1862 | -2.3276 | 0.0491 | 0.0551 | 5.2400 | 3.2400 | 3.2400 | 0.1510 | 0.0356 | 1 | 0.0190 | 5.2083 | 90.6250 | 1 | 0.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_h96` | 5 | 5 | 0 | 97.2000 | 92 | 103 | -2.1853 | -0.1748 | 0.0490 | 0.0707 | 3.2400 | 3.2400 | 0.0280 | 0.6000 | 0.0072 | 5.0977 | 93.0284 | 1.0000 | 0.6000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
