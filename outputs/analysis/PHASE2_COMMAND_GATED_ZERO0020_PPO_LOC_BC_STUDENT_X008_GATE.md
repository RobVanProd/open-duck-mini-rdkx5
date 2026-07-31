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
| `ppo_loc_command_gated` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 663 | `fall_or_nan` | -0.0018 | -0.0230 | 0.1802 | 0.0636 | 1.5989 | 0.0000 | 0.0000 | 0.1776 | 0.0350 | 9 | 0.0198 | 22.3228 | 77.3756 | 10 | 1.0000 |
| `ppo_loc_command_gated` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0265 | 0.3314 | 0.1797 | 0.1582 | 1.5995 | 0.0000 | 0.0000 | 0.1862 | 0.0159 | 11 | 0.0253 | 23.8667 | 76.1333 | 13 | 1.0000 |
| `ppo_loc_command_gated` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0253 | 0.3159 | 0.1957 | 0.1556 | 1.5981 | 0.0000 | 0.0000 | 0.1874 | 0.0169 | 11 | 0.0278 | 23.3333 | 76.6667 | 13 | 0.9231 |
| `ppo_loc_command_gated` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0216 | 0.2696 | 0.1926 | 0.1582 | 1.5905 | 0.0000 | 0.0000 | 0.1843 | 0.0142 | 10 | 0.0267 | 22.9333 | 77.0667 | 13 | 0.9231 |
| `ppo_loc_command_gated` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 750 | `fall_or_nan` | -0.0011 | -0.0140 | 0.1700 | 0.0737 | 1.5939 | 0.0000 | 0.0000 | 0.1752 | 0.0333 | 11 | 0.0199 | 20.1333 | 79.6000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_command_gated` | 5 | 2 | 3 | 732.6000 | 663 | 750 | 0.1760 | 0.0141 | 0.1836 | 0.1219 | 0.0000 | 0.0000 | 0.0231 | 10.4000 | 0.0239 | 22.5179 | 77.3684 | 11.8000 | 0.9492 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
