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
seeds: `[0, 1, 3, 5, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[0, 1, 3, 5, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed4_right_swing_phasecmd` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0021 | 0.0257 | 0.0151 | 0.1519 | 0.3631 | 0.0000 | 0.0624 | 0.0209 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |
| `seed4_right_swing_phasecmd` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0049 | 0.0610 | 0.0617 | 0.1563 | 1.2628 | 0.0000 | 0.1212 | 0.0121 | 1 | 0.0070 | 7.6000 | 92.0000 | 0 | NA |
| `seed4_right_swing_phasecmd` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 250 | `duration_complete` | 0.0315 | 0.3937 | 0.1271 | 0.1555 | 2.2582 | 0.0324 | 0.1912 | 0.0121 | 6 | 0.0105 | 25.2000 | 74.8000 | 0 | NA |
| `seed4_right_swing_phasecmd` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0101 | 0.1257 | 0.0249 | 0.1464 | 0.9486 | 0.0000 | 0.1060 | 0.0194 | 1 | 0.0033 | 1.2000 | 98.0000 | 0 | NA |
| `seed4_right_swing_phasecmd` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0024 | 0.0297 | 0.0498 | 0.1564 | 1.2272 | 0.0000 | 0.1147 | 0.0015 | 1 | 0.0016 | 3.6000 | 96.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed4_right_swing_phasecmd` | 5 | 0 | 5 | 250.0000 | 250 | 250 | 0.1271 | 0.0102 | 0.0557 | 0.1533 | 0.0065 | 0.0132 | 1.8000 | 0.0045 | 7.6800 | 92.0800 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
