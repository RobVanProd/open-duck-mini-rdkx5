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
| `ppo_loc_seed07_weighted` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 216 | `fall_or_nan` | 0.1026 | 1.2822 | 0.6539 | 0.0187 | 1.5725 | 0.0000 | 0.0000 | 0.1936 | 0.0399 | 2 | 0.0250 | 19.9074 | 80.0926 | 3 | 1.0000 |
| `ppo_loc_seed07_weighted` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0249 | 0.3117 | 0.1902 | 0.1560 | 1.6052 | 0.0000 | 0.0000 | 0.1931 | 0.0155 | 10 | 0.0175 | 21.6000 | 78.4000 | 13 | 1.0000 |
| `ppo_loc_seed07_weighted` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 711 | `fall_or_nan` | -0.0021 | -0.0258 | 0.2006 | 0.0612 | 1.6128 | 0.0000 | 0.1877 | 0.1845 | 0.0349 | 10 | 0.0129 | 23.3474 | 76.3713 | 12 | 0.9167 |
| `ppo_loc_seed07_weighted` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0229 | 0.2861 | 0.1892 | 0.1572 | 1.6090 | 0.0000 | 0.0000 | 0.1945 | 0.0128 | 9 | 0.0209 | 21.8667 | 78.1333 | 13 | 0.9231 |
| `ppo_loc_seed07_weighted` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0273 | 0.3409 | 0.1743 | 0.1572 | 1.6063 | 0.0000 | 0.0000 | 0.1885 | 0.0122 | 12 | 0.0213 | 23.7333 | 76.2667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_seed07_weighted` | 5 | 2 | 3 | 635.4000 | 216 | 750 | 0.4390 | 0.0351 | 0.2816 | 0.1100 | 0.0000 | 0.0375 | 0.0230 | 8.6000 | 0.0195 | 22.0910 | 77.8528 | 10.2000 | 0.9679 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
