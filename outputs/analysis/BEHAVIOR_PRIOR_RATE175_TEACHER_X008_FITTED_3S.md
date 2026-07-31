# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `3.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `None`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 0 | `PASS_CANDIDATE_SIM_GATE` | 150 | `duration_complete` | 0.0209 | 0.2617 | 0.0638 | 0.1536 | 1.6881 | 0.0000 | 0.1946 | 0.0085 | 2 | 0.0011 | 22.0000 | 78.0000 | 0 | NA |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0172 | 0.2156 | 0.0020 | 0.0817 | 1.2187 | 0.0000 | 0.2753 | 0.0126 | 0 | 0.0000 | 84.8485 | 6.0606 | 0 | NA |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 150 | `duration_complete` | 0.0076 | 0.0953 | 0.0162 | 0.1525 | 0.9884 | 0.0000 | 0.1157 | 0.0054 | 1 | 0.0056 | 6.6667 | 93.3333 | 0 | NA |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 150 | `duration_complete` | -0.0092 | -0.1145 | 0.0779 | 0.1588 | 0.9090 | 0.0000 | 0.1158 | 0.0222 | 1 | 0.0033 | 4.0000 | 93.3333 | 0 | NA |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 4 | `PASS_CANDIDATE_SIM_GATE` | 150 | `duration_complete` | 0.0238 | 0.2970 | 0.0638 | 0.1515 | 1.5844 | 0.0000 | 0.1763 | 0.0072 | 2 | 0.0047 | 12.0000 | 88.0000 | 0 | NA |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 5 | `PASS_CANDIDATE_SIM_GATE` | 150 | `duration_complete` | 0.0294 | 0.3681 | 0.0690 | 0.1468 | 1.6658 | 0.0000 | 0.1874 | 0.0192 | 2 | 0.0054 | 7.3333 | 91.3333 | 0 | NA |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 150 | `duration_complete` | 0.0096 | 0.1202 | 0.0633 | 0.1587 | 1.6134 | 0.0000 | 0.1747 | 0.0163 | 1 | 0.0077 | 15.3333 | 84.0000 | 0 | NA |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | 0.0133 | 0.1660 | 0.0001 | 0.0674 | 1.6187 | 0.0000 | 0.3041 | 0.0106 | 0 | 0.0000 | 85.2941 | 8.8235 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 8 | 2 | 6 | 120.8750 | 33 | 150 | 0.1762 | 0.0141 | 0.0445 | 0.1339 | 0.0000 | 0.0127 | 1.1250 | 0.0035 | 29.6845 | 67.8605 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
