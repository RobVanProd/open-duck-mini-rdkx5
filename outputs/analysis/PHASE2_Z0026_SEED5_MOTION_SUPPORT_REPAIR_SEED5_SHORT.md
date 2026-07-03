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
seeds: `[5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0026`
reset_settle_ticks: `0`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ckpt40960` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | `fall_or_nan` | -0.2219 | -2.7736 | 0.0826 | 0.0733 | 1.7289 | 0.0000 | 0.0000 | 0.2032 | 0.0196 | 1 | 0.0036 | 12.3077 | 84.6154 | 0 | NA |
| `ckpt81920` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | `fall_or_nan` | -0.2262 | -2.8270 | 0.0826 | 0.0687 | 1.7510 | 0.0000 | 0.0000 | 0.2034 | 0.0327 | 1 | 0.0036 | 13.8462 | 81.5385 | 0 | NA |
| `ckpt122880` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 64 | `fall_or_nan` | -0.2184 | -2.7300 | 0.0802 | 0.0806 | 1.7437 | 0.0000 | 0.0000 | 0.2019 | 0.0331 | 2 | 0.0150 | 12.5000 | 81.2500 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ckpt40960` | 1 | 1 | 0 | 65.0000 | 65 | 65 | -2.7736 | -0.2219 | 0.0826 | 0.0733 | 0.0000 | 0.0000 | 0.0196 | 1.0000 | 0.0036 | 12.3077 | 84.6154 | 0.0000 | NA |
| `ckpt81920` | 1 | 1 | 0 | 65.0000 | 65 | 65 | -2.8270 | -0.2262 | 0.0826 | 0.0687 | 0.0000 | 0.0000 | 0.0327 | 1.0000 | 0.0036 | 13.8462 | 81.5385 | 0.0000 | NA |
| `ckpt122880` | 1 | 1 | 0 | 64.0000 | 64 | 64 | -2.7300 | -0.2184 | 0.0802 | 0.0806 | 0.0000 | 0.0000 | 0.0331 | 2.0000 | 0.0150 | 12.5000 | 81.2500 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
