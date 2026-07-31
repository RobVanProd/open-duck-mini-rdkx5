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
| `live_iter2_ppo_loc` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0231 | 0.2891 | 0.1991 | 0.1575 | 1.5933 | 0.0000 | 0.0000 | 0.1906 | 0.0175 | 7 | 0.0172 | 18.4000 | 81.6000 | 12 | 0.9167 |
| `live_iter2_ppo_loc` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0216 | 0.2700 | 0.1931 | 0.1579 | 1.6215 | 0.0000 | 0.0000 | 0.1867 | 0.0171 | 11 | 0.0191 | 19.3333 | 80.6667 | 13 | 1.0000 |
| `live_iter2_ppo_loc` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0226 | 0.2826 | 0.1881 | 0.1581 | 1.5999 | 0.0000 | 0.0000 | 0.1874 | 0.0172 | 15 | 0.0169 | 21.4667 | 78.5333 | 13 | 0.9231 |
| `live_iter2_ppo_loc` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 341 | `fall_or_nan` | -0.0322 | -0.4030 | 0.2006 | 0.0731 | 1.6251 | 0.0000 | 0.0000 | 0.1838 | 0.0334 | 5 | 0.0200 | 14.9560 | 84.7507 | 6 | 0.8333 |
| `live_iter2_ppo_loc` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0221 | 0.2758 | 0.1841 | 0.1577 | 1.6079 | 0.0000 | 0.0000 | 0.1898 | 0.0145 | 10 | 0.0138 | 21.4667 | 78.5333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_iter2_ppo_loc` | 5 | 1 | 4 | 668.2000 | 341 | 750 | 0.1429 | 0.0114 | 0.1930 | 0.1408 | 0.0000 | 0.0000 | 0.0199 | 9.6000 | 0.0174 | 19.1245 | 80.8168 | 10.8000 | 0.9346 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
