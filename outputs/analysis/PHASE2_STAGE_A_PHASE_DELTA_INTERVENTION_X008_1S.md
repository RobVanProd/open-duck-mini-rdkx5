# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `1.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `None`
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_delta` | 0 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0343 | 0.4288 | 0.0812 | 0.1520 | 1.6637 | 0.0000 | 0.0000 | 0.2392 | 0.0038 | 0 | 0.0000 | 14.0000 | 86.0000 | 0 | NA |
| `phase_delta` | 1 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0333 | 0.4158 | 0.1097 | 0.1556 | 1.7086 | 0.0000 | 0.0000 | 0.2242 | 0.0122 | 1 | 0.0027 | 30.0000 | 68.0000 | 0 | NA |
| `phase_delta` | 2 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0499 | 0.6242 | 0.1099 | 0.1509 | 1.7506 | 0.0000 | 0.0000 | 0.2377 | 0.0056 | 3 | 0.0051 | 26.0000 | 74.0000 | 0 | NA |
| `phase_delta` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0304 | -0.3806 | 0.2258 | 0.1550 | 1.6181 | 0.0000 | 0.0000 | 0.1828 | 0.0126 | 1 | 0.0017 | 12.0000 | 84.0000 | 0 | NA |
| `phase_delta` | 4 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0477 | 0.5967 | 0.0357 | 0.1506 | 1.6881 | 0.0000 | 0.0000 | 0.1860 | 0.0031 | 0 | 0.0000 | 8.0000 | 92.0000 | 0 | NA |
| `phase_delta` | 5 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0527 | 0.6593 | 0.0178 | 0.1462 | 1.2448 | 0.0000 | 0.0000 | 0.2312 | 0.0190 | 1 | 0.0037 | 8.0000 | 88.0000 | 0 | NA |
| `phase_delta` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0013 | 0.0157 | 0.0392 | 0.1557 | 1.6557 | 0.0000 | 0.0000 | 0.1833 | 0.0159 | 1 | 0.0129 | 28.0000 | 72.0000 | 0 | NA |
| `phase_delta` | 7 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0237 | 0.2966 | 0.0584 | 0.1559 | 1.5666 | 0.0000 | 0.0000 | 0.2187 | 0.0119 | 0 | 0.0000 | 16.0000 | 84.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_delta` | 8 | 0 | 8 | 50.0000 | 50 | 50 | 0.3320 | 0.0266 | 0.0847 | 0.1527 | 0.0000 | 0.0000 | 0.0105 | 0.8750 | 0.0033 | 17.7500 | 81.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
