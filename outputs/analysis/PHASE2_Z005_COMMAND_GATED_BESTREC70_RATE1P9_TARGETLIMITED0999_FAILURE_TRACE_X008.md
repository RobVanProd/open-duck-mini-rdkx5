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
seeds: `[1, 5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[1, 5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 711 | `fall_or_nan` | 0.0565 | 0.7064 | 0.2479 | 0.0045 | 1.9242 | 0.0000 | 0.0000 | 0.1880 | 0.0592 | 14 | 0.0186 | 25.3165 | 74.4023 | 0 | NA |
| `limited` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.2711 | -3.3886 | 0.0707 | 0.0594 | 1.9015 | 0.0000 | 0.0000 | 0.1897 | 0.0321 | 1 | 0.0105 | 8.7719 | 82.4561 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 2 | 2 | 0 | 384.0000 | 57 | 711 | -1.3411 | -0.1073 | 0.1593 | 0.0320 | 0.0000 | 0.0000 | 0.0457 | 7.5000 | 0.0146 | 17.0442 | 78.4292 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
