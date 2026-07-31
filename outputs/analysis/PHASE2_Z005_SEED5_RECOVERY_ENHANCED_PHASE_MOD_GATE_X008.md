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
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `enhanced_phase_mod` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0242 | 0.3020 | 0.1223 | 0.1527 | 2.0233 | 0.0000 | 0.2681 | 0.1942 | 0.0119 | 18 | 0.0057 | 19.6000 | 80.4000 | 0 | NA |
| `enhanced_phase_mod` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0297 | 0.3715 | 0.1451 | 0.1565 | 2.0178 | 0.0000 | 0.0471 | 0.1887 | 0.0128 | 20 | 0.0084 | 24.4000 | 75.4667 | 0 | NA |
| `enhanced_phase_mod` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0297 | 0.3717 | 0.1235 | 0.1514 | 2.0147 | 0.0000 | 0.0120 | 0.1907 | 0.0123 | 13 | 0.0159 | 23.0667 | 76.9333 | 0 | NA |
| `enhanced_phase_mod` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 74 | `fall_or_nan` | -0.2616 | -3.2700 | 0.1599 | 0.0589 | 2.0359 | 0.0000 | 0.7463 | 0.1522 | 0.0288 | 0 | 0.0000 | 9.4595 | 90.5405 | 0 | NA |
| `enhanced_phase_mod` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0299 | 0.3736 | 0.1162 | 0.1508 | 2.0290 | 0.0000 | 0.1369 | 0.1887 | 0.0112 | 15 | 0.0108 | 23.0667 | 76.9333 | 0 | NA |
| `enhanced_phase_mod` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 52 | `fall_or_nan` | -0.2758 | -3.4474 | 0.0604 | 0.0749 | 2.0176 | 0.0000 | 0.0000 | 0.2312 | 0.0313 | 1 | 0.0093 | 9.6154 | 84.6154 | 0 | NA |
| `enhanced_phase_mod` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0289 | 0.3609 | 0.1180 | 0.1532 | 2.0227 | 0.0000 | 0.1375 | 0.1881 | 0.0179 | 18 | 0.0166 | 23.3333 | 76.6667 | 0 | NA |
| `enhanced_phase_mod` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0266 | 0.3328 | 0.1219 | 0.1564 | 2.0058 | 0.0000 | 0.0787 | 0.1916 | 0.0129 | 9 | 0.0148 | 22.0000 | 78.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `enhanced_phase_mod` | 8 | 2 | 6 | 578.2500 | 52 | 750 | -0.5756 | -0.0460 | 0.1209 | 0.1319 | 0.0000 | 0.1783 | 0.0174 | 11.7500 | 0.0102 | 19.3177 | 79.9445 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
