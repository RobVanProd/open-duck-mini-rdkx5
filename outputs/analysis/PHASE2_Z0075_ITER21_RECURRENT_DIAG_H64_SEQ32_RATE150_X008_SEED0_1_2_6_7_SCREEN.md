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
seeds: `[0, 1, 2, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_diag` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0009 | 0.0106 | 0.0672 | 0.1612 | 0.0772 | 0.0000 | 0.0000 | 0.0420 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `recurrent_diag` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0009 | 0.0118 | 0.0723 | 0.1607 | 0.0768 | 0.0000 | 0.0000 | 0.0430 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `recurrent_diag` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0009 | 0.0113 | 0.0684 | 0.1613 | 0.0784 | 0.0000 | 0.0000 | 0.0433 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `recurrent_diag` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0008 | 0.0104 | 0.0732 | 0.1611 | 0.0773 | 0.0000 | 0.0000 | 0.0424 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `recurrent_diag` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0008 | 0.0106 | 0.0694 | 0.1611 | 0.0754 | 0.0000 | 0.0000 | 0.0411 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_diag` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.0109 | 0.0009 | 0.0701 | 0.1611 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.2000 | 0.9172 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
