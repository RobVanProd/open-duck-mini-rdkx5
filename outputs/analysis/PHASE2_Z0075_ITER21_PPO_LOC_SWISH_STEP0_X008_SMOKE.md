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
seeds: `[0, 1, 5]`
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
| `ppo_loc_swish_step0` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 667 | `fall_or_nan` | -0.0003 | -0.0042 | 0.1679 | 0.0653 | 1.5423 | 0.0000 | 0.0000 | 0.1776 | 0.0326 | 11 | 0.0162 | 22.3388 | 77.3613 | 10 | 0.9000 |
| `ppo_loc_swish_step0` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0259 | 0.3243 | 0.1916 | 0.1580 | 1.5487 | 0.0000 | 0.0000 | 0.1884 | 0.0156 | 9 | 0.0240 | 22.0000 | 78.0000 | 13 | 0.9231 |
| `ppo_loc_swish_step0` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0276 | 0.3450 | 0.1872 | 0.1580 | 1.5428 | 0.0000 | 0.0000 | 0.1855 | 0.0120 | 11 | 0.0331 | 24.4000 | 75.6000 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_swish_step0` | 3 | 1 | 2 | 722.3333 | 667 | 750 | 0.2217 | 0.0177 | 0.1822 | 0.1271 | 0.0000 | 0.0000 | 0.0201 | 10.3333 | 0.0244 | 22.9129 | 76.9871 | 12.0000 | 0.9154 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
