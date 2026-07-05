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
| `live_iter1_ppo_loc` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0263 | 0.3285 | 0.1790 | 0.1580 | 1.6751 | 0.0000 | 0.0000 | 0.1855 | 0.0154 | 10 | 0.0203 | 22.9333 | 77.0667 | 12 | 0.9167 |
| `live_iter1_ppo_loc` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0269 | 0.3365 | 0.1783 | 0.1580 | 1.6686 | 0.0000 | 0.0000 | 0.1893 | 0.0156 | 14 | 0.0190 | 24.0000 | 76.0000 | 13 | 1.0000 |
| `live_iter1_ppo_loc` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0248 | 0.3096 | 0.1914 | 0.1580 | 1.6732 | 0.0000 | 0.0000 | 0.1909 | 0.0180 | 10 | 0.0297 | 22.1333 | 77.8667 | 13 | 0.9231 |
| `live_iter1_ppo_loc` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 392 | `fall_or_nan` | 0.0759 | 0.9484 | 0.3997 | -0.0018 | 1.6381 | 0.0000 | 0.0000 | 0.1939 | 0.0591 | 10 | 0.0284 | 25.2551 | 74.7449 | 7 | 0.8571 |
| `live_iter1_ppo_loc` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0307 | 0.3835 | 0.1977 | 0.1571 | 1.6553 | 0.0000 | 0.0000 | 0.1932 | 0.0165 | 15 | 0.0165 | 25.3333 | 74.6667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_iter1_ppo_loc` | 5 | 1 | 4 | 678.4000 | 392 | 750 | 0.4613 | 0.0369 | 0.2292 | 0.1259 | 0.0000 | 0.0000 | 0.0249 | 11.8000 | 0.0228 | 23.9310 | 76.0690 | 11.0000 | 0.9394 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
