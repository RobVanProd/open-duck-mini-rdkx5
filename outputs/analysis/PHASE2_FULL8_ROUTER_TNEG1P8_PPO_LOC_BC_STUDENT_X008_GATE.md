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
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_router_tneg1p8_ppo_loc` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3562 | 0.1711 | 0.1593 | 1.5666 | 0.0000 | 0.0000 | 0.1862 | 0.0142 | 13 | 0.0169 | 24.4000 | 75.6000 | 12 | 0.9167 |
| `full8_router_tneg1p8_ppo_loc` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0305 | 0.3810 | 0.1703 | 0.1592 | 1.5565 | 0.0000 | 0.0000 | 0.1877 | 0.0158 | 13 | 0.0160 | 25.3333 | 74.6667 | 13 | 1.0000 |
| `full8_router_tneg1p8_ppo_loc` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0335 | 0.4191 | 0.1802 | 0.1574 | 1.5567 | 0.0000 | 0.0000 | 0.1828 | 0.0169 | 18 | 0.0219 | 28.2667 | 71.7333 | 13 | 0.9231 |
| `full8_router_tneg1p8_ppo_loc` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0294 | 0.3673 | 0.1734 | 0.1587 | 1.5602 | 0.0000 | 0.0000 | 0.1854 | 0.0123 | 17 | 0.0214 | 26.0000 | 74.0000 | 13 | 1.0000 |
| `full8_router_tneg1p8_ppo_loc` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0322 | 0.4020 | 0.1867 | 0.1574 | 1.5604 | 0.0000 | 0.0000 | 0.1864 | 0.0163 | 19 | 0.0215 | 28.8000 | 71.2000 | 12 | 1.0000 |
| `full8_router_tneg1p8_ppo_loc` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 213 | `fall_or_nan` | 0.1134 | 1.4177 | 0.7321 | -0.0065 | 1.5577 | 0.0000 | 0.0000 | 0.1938 | 0.0591 | 3 | 0.0272 | 19.7183 | 78.8732 | 3 | 1.0000 |
| `full8_router_tneg1p8_ppo_loc` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 533 | `fall_or_nan` | -0.0060 | -0.0752 | 0.1820 | 0.0749 | 1.5572 | 0.0000 | 0.0000 | 0.1815 | 0.0358 | 10 | 0.0197 | 24.2026 | 75.4221 | 9 | 0.8889 |
| `full8_router_tneg1p8_ppo_loc` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3823 | 0.2054 | 0.1583 | 1.5700 | 0.0000 | 0.0000 | 0.1857 | 0.0167 | 14 | 0.0217 | 25.4667 | 74.5333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_router_tneg1p8_ppo_loc` | 8 | 2 | 6 | 655.7500 | 213 | 750 | 0.4563 | 0.0365 | 0.2502 | 0.1273 | 0.0000 | 0.0000 | 0.0234 | 13.3750 | 0.0208 | 25.2735 | 74.5036 | 10.6250 | 0.9661 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
