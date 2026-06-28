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
| `live_oracle_iter0` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0489 | 0.6112 | 0.1004 | 0.1511 | 3.6065 | 0.8565 | 0.2593 | 0.0121 | 8 | 0.0103 | 36.0000 | 64.0000 | 0 | NA |
| `live_oracle_iter0` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0471 | 0.5890 | 0.0898 | 0.1506 | 3.6914 | 0.9414 | 0.2521 | 0.0117 | 6 | 0.0155 | 29.6000 | 70.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_iter0` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.6001 | 0.0480 | 0.0951 | 0.1509 | 0.8989 | 0.0119 | 7.0000 | 0.0129 | 32.8000 | 67.2000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
