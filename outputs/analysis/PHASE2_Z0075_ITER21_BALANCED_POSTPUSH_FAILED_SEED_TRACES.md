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
seeds: `[6, 7]`
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
trace_seeds: `[6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_balanced_postpush` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 212 | `fall_or_nan` | 0.1178 | 1.4723 | 0.7550 | -0.0091 | 1.5925 | 0.0000 | 0.0000 | 0.1962 | 0.0581 | 4 | 0.0190 | 19.3396 | 78.3019 | 3 | 0.6667 |
| `iter21_balanced_postpush` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 619 | `fall_or_nan` | 0.0573 | 0.7163 | 0.3036 | -0.0075 | 1.5840 | 0.0000 | 0.0000 | 0.1897 | 0.0607 | 12 | 0.0246 | 25.5250 | 73.9903 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_balanced_postpush` | 2 | 2 | 0 | 415.5000 | 212 | 619 | 1.0943 | 0.0875 | 0.5293 | -0.0083 | 0.0000 | 0.0000 | 0.0594 | 8.0000 | 0.0218 | 22.4323 | 76.1461 | 5.5000 | 0.7708 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
