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
| `live_oracle_iter1_ppo_loc` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0278 | 0.3473 | 0.1992 | 0.1583 | 1.6081 | 0.0000 | 0.0000 | 0.1954 | 0.0204 | 15 | 0.0272 | 23.2000 | 76.8000 | 12 | 0.9167 |
| `live_oracle_iter1_ppo_loc` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0332 | 0.4153 | 0.1870 | 0.1589 | 1.5948 | 0.0000 | 0.0000 | 0.1898 | 0.0180 | 18 | 0.0237 | 28.5333 | 71.4667 | 13 | 1.0000 |
| `live_oracle_iter1_ppo_loc` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0267 | 0.3332 | 0.1795 | 0.1576 | 1.5894 | 0.0000 | 0.0000 | 0.1887 | 0.0164 | 17 | 0.0174 | 24.4000 | 75.6000 | 13 | 0.9231 |
| `live_oracle_iter1_ppo_loc` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0229 | 0.2865 | 0.1700 | 0.1591 | 1.6000 | 0.0000 | 0.0000 | 0.1842 | 0.0119 | 13 | 0.0214 | 23.7333 | 76.2667 | 13 | 1.0000 |
| `live_oracle_iter1_ppo_loc` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 564 | `fall_or_nan` | 0.0592 | 0.7396 | 0.3174 | 0.0018 | 1.6132 | 0.0000 | 0.7025 | 0.1929 | 0.0594 | 12 | 0.0187 | 21.9858 | 77.4823 | 9 | 1.0000 |
| `live_oracle_iter1_ppo_loc` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0279 | 0.3491 | 0.1993 | 0.1566 | 1.5963 | 0.0000 | 0.0000 | 0.1904 | 0.0207 | 14 | 0.0224 | 25.6000 | 74.4000 | 13 | 1.0000 |
| `live_oracle_iter1_ppo_loc` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 584 | `fall_or_nan` | -0.0055 | -0.0682 | 0.1720 | 0.0698 | 1.6135 | 0.0000 | 0.0000 | 0.1855 | 0.0342 | 12 | 0.0164 | 22.9452 | 76.7123 | 10 | 0.9000 |
| `live_oracle_iter1_ppo_loc` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0263 | 0.3293 | 0.1860 | 0.1592 | 1.6114 | 0.0000 | 0.0000 | 0.1931 | 0.0193 | 13 | 0.0220 | 22.2667 | 77.7333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_iter1_ppo_loc` | 8 | 2 | 6 | 706.0000 | 564 | 750 | 0.3415 | 0.0273 | 0.2013 | 0.1277 | 0.0000 | 0.0878 | 0.0250 | 14.2500 | 0.0212 | 24.0830 | 75.8077 | 11.6250 | 0.9675 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
