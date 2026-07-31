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
seeds: `[1, 3, 5]`
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
trace_seeds: `[1, 3, 5]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_rate150_settle10` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0317 | 0.3964 | 0.1916 | 0.1576 | 1.6221 | 0.0000 | 0.0583 | 0.1850 | 0.0187 | 14 | 0.0179 | 24.5333 | 75.4667 | 13 | 0.9231 |
| `iter21_rate150_settle10` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0281 | 0.3514 | 0.1589 | 0.1587 | 1.6129 | 0.0000 | 0.0097 | 0.1791 | 0.0147 | 16 | 0.0144 | 24.8000 | 75.2000 | 13 | 0.9231 |
| `iter21_rate150_settle10` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 599 | `fall_or_nan` | -0.0054 | -0.0672 | 0.1735 | 0.0630 | 1.6282 | 0.0000 | 0.0000 | 0.1786 | 0.0337 | 11 | 0.0170 | 23.2053 | 76.4608 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_rate150_settle10` | 3 | 1 | 2 | 699.6667 | 599 | 750 | 0.2269 | 0.0181 | 0.1747 | 0.1265 | 0.0000 | 0.0227 | 0.0224 | 13.6667 | 0.0164 | 24.1796 | 75.7091 | 12.0000 | 0.9154 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
