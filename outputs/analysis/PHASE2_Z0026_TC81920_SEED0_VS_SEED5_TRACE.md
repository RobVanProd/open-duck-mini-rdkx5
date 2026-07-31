# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `2.0`
seeds: `[0, 5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0026`
reset_settle_ticks: `0`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `tc81920` | 0 | `HOLD_CANDIDATE_TRACKING` | 100 | `duration_complete` | 0.0250 | 0.3128 | 0.1232 | 0.1519 | 1.7138 | 0.0000 | 0.0000 | 0.2129 | 0.0133 | 1 | 0.0033 | 13.0000 | 87.0000 | 0 | NA |
| `tc81920` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | `fall_or_nan` | -0.2279 | -2.8483 | 0.0826 | 0.0667 | 1.8401 | 0.0000 | 0.0000 | 0.2022 | 0.0331 | 2 | 0.0083 | 9.2308 | 83.0769 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `tc81920` | 2 | 1 | 1 | 82.5000 | 65 | 100 | -1.2677 | -0.1014 | 0.1029 | 0.1093 | 0.0000 | 0.0000 | 0.0232 | 1.5000 | 0.0058 | 11.1154 | 85.0385 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
