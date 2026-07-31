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
| `full8_rich_parent` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3306 | 0.2130 | 0.1582 | 1.5893 | 0.0000 | 0.0000 | 0.1870 | 0.0174 | 14 | 0.0203 | 22.1333 | 77.8667 | 12 | 0.9167 |
| `full8_rich_parent` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 149 | `fall_or_nan` | 0.1421 | 1.7761 | 0.8855 | 0.0014 | 1.5789 | 0.0000 | 0.0000 | 0.2014 | 0.0582 | 1 | 0.0073 | 9.3960 | 89.2617 | 2 | 1.0000 |
| `full8_rich_parent` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0277 | 0.3468 | 0.1729 | 0.1582 | 1.5962 | 0.0000 | 0.0000 | 0.1882 | 0.0135 | 15 | 0.0185 | 24.6667 | 75.3333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_rich_parent` | 3 | 1 | 2 | 549.6667 | 149 | 750 | 0.8178 | 0.0654 | 0.4238 | 0.1059 | 0.0000 | 0.0000 | 0.0297 | 10.0000 | 0.0154 | 18.7320 | 80.8206 | 8.0000 | 0.9722 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
