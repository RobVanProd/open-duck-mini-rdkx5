# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[2, 4]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[2, 4]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter2_ppo_shape_bc` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0510 | 0.6379 | 0.1038 | 0.1511 | 3.6283 | 0.8783 | 0.2546 | 0.0120 | 9 | 0.0080 | 39.2000 | 60.8000 | 0 | NA |
| `iter2_ppo_shape_bc` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0486 | 0.6080 | 0.0961 | 0.1506 | 3.5627 | 0.8127 | 0.2552 | 0.0109 | 7 | 0.0151 | 32.4000 | 67.6000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter2_ppo_shape_bc` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.6229 | 0.0498 | 0.0999 | 0.1509 | 0.8455 | 0.0114 | 8.0000 | 0.0116 | 35.8000 | 64.2000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
