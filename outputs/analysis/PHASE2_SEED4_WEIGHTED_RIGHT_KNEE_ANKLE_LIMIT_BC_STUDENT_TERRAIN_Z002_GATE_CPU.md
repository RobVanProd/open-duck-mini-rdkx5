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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed4w_right_knee_ankle_limited` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0372 | 0.4652 | 0.1109 | 0.1511 | 2.2634 | 0.0000 | 0.1985 | 0.0112 | 6 | 0.0086 | 25.6000 | 74.4000 | 0 | NA |
| `seed4w_right_knee_ankle_limited` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0359 | 0.4484 | 0.0970 | 0.1506 | 2.3359 | 0.0000 | 0.2010 | 0.0105 | 2 | 0.0061 | 21.6000 | 78.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed4w_right_knee_ankle_limited` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.4568 | 0.0365 | 0.1040 | 0.1509 | 0.0000 | 0.0109 | 4.0000 | 0.0074 | 23.6000 | 76.4000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
