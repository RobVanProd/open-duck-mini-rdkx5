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
seeds: `[0, 3, 4, 6]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0025`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `contactphase` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0322 | 0.4022 | 0.1099 | 0.1519 | 2.2779 | 0.0000 | 0.6004 | 0.1953 | 0.0119 | 14 | 0.0179 | 24.6667 | 75.3333 | 0 | NA |
| `contactphase` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0305 | 0.3810 | 0.1151 | 0.1550 | 2.3107 | 0.0000 | 0.4152 | 0.1905 | 0.0121 | 18 | 0.0196 | 25.4667 | 74.5333 | 0 | NA |
| `contactphase` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0349 | 0.4364 | 0.1069 | 0.1506 | 2.3446 | 0.0000 | 0.5087 | 0.1921 | 0.0116 | 21 | 0.0044 | 26.5333 | 73.4667 | 0 | NA |
| `contactphase` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0372 | 0.4645 | 0.1069 | 0.1531 | 2.3288 | 0.0000 | 0.4916 | 0.1911 | 0.0175 | 19 | 0.0060 | 28.1333 | 71.8667 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `contactphase` | 4 | 0 | 4 | 750.0000 | 750 | 750 | 0.4211 | 0.0337 | 0.1097 | 0.1527 | 0.0000 | 0.5040 | 0.0133 | 18.0000 | 0.0120 | 26.2000 | 73.8000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
