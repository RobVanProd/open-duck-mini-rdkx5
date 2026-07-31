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
| `ppo_step0_seed5_weighted` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 644 | `fall_or_nan` | 0.0552 | 0.6902 | 0.2433 | 0.0089 | 1.5115 | 0.0000 | 0.0000 | 0.1855 | 0.0603 | 14 | 0.0206 | 24.3789 | 75.3106 | 10 | 0.9000 |
| `ppo_step0_seed5_weighted` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0298 | 0.3731 | 0.1870 | 0.1581 | 1.5169 | 0.0000 | 0.0000 | 0.1885 | 0.0156 | 15 | 0.0236 | 26.9333 | 73.0667 | 13 | 0.9231 |
| `ppo_step0_seed5_weighted` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0295 | 0.3692 | 0.1830 | 0.1593 | 1.5231 | 0.0000 | 0.0000 | 0.1905 | 0.0164 | 16 | 0.0208 | 27.3333 | 72.6667 | 13 | 0.9231 |
| `ppo_step0_seed5_weighted` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0263 | 0.3283 | 0.1758 | 0.1581 | 1.5210 | 0.0000 | 0.0000 | 0.1886 | 0.0119 | 13 | 0.0240 | 23.4667 | 76.5333 | 13 | 0.9231 |
| `ppo_step0_seed5_weighted` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3272 | 0.1816 | 0.1581 | 1.5213 | 0.0000 | 0.0000 | 0.1893 | 0.0147 | 16 | 0.0222 | 25.2000 | 74.8000 | 12 | 0.9167 |
| `ppo_step0_seed5_weighted` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0287 | 0.3583 | 0.1753 | 0.1592 | 1.5161 | 0.0000 | 0.0000 | 0.1873 | 0.0116 | 8 | 0.0254 | 24.6667 | 75.3333 | 13 | 0.9231 |
| `ppo_step0_seed5_weighted` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0298 | 0.3727 | 0.1979 | 0.1577 | 1.5172 | 0.0000 | 0.0000 | 0.1864 | 0.0160 | 14 | 0.0247 | 25.6000 | 74.4000 | 13 | 0.9231 |
| `ppo_step0_seed5_weighted` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0279 | 0.3490 | 0.1863 | 0.1594 | 1.5220 | 0.0000 | 0.0000 | 0.1891 | 0.0188 | 13 | 0.0282 | 23.6000 | 76.4000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0_seed5_weighted` | 8 | 1 | 7 | 736.7500 | 644 | 750 | 0.3960 | 0.0317 | 0.1913 | 0.1399 | 0.0000 | 0.0000 | 0.0206 | 13.6250 | 0.0237 | 25.1474 | 74.8138 | 12.1250 | 0.9165 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
