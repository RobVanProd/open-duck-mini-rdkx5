# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed7_weighted_student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0235 | NA | 0.1964 | 0.1581 | 1.6073 | 0.0000 | 0.0000 | 0.1823 | 0.0174 | 8 | 0.0240 | 21.8667 | 78.1333 | 12 | 0.9167 |
| `seed7_weighted_student` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 147 | `fall_or_nan` | 0.1431 | NA | 0.9095 | 0.0048 | 1.5808 | 0.0000 | 0.0000 | 0.2004 | 0.0602 | 2 | 0.0035 | 12.2449 | 87.0748 | 2 | 1.0000 |
| `seed7_weighted_student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0295 | NA | 0.1909 | 0.1581 | 1.6024 | 0.0000 | 0.0000 | 0.1871 | 0.0191 | 15 | 0.0189 | 27.6000 | 72.4000 | 13 | 0.9231 |
| `seed7_weighted_student` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 206 | `fall_or_nan` | 0.1107 | NA | 0.7060 | -0.0007 | 1.5530 | 0.0000 | 0.0000 | 0.1900 | 0.0591 | 4 | 0.0088 | 18.9320 | 80.5825 | 3 | 1.0000 |
| `seed7_weighted_student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0259 | NA | 0.1725 | 0.1581 | 1.6079 | 0.0000 | 0.0000 | 0.1913 | 0.0130 | 10 | 0.0191 | 22.2667 | 77.7333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed7_weighted_student` | 5 | 2 | 3 | 520.6000 | 147 | 750 | NA | 0.0665 | 0.4351 | 0.0957 | 0.0000 | 0.0000 | 0.0338 | 7.8000 | 0.0149 | 20.5821 | 79.1848 | 8.0000 | 0.9679 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
