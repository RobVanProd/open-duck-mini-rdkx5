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
| `ppo_step0` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0280 | 0.3495 | 0.1734 | 0.1591 | 1.5192 | 0.0000 | 0.0000 | 0.1809 | 0.0158 | 15 | 0.0126 | 24.9333 | 75.0667 | 12 | 0.9167 |
| `ppo_step0` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3515 | 0.1705 | 0.1589 | 1.5160 | 0.0000 | 0.0000 | 0.1848 | 0.0157 | 18 | 0.0238 | 25.7333 | 74.2667 | 13 | 0.9231 |
| `ppo_step0` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0270 | 0.3377 | 0.1794 | 0.1582 | 1.5213 | 0.0000 | 0.0000 | 0.1814 | 0.0160 | 14 | 0.0210 | 24.5333 | 75.4667 | 13 | 0.9231 |
| `ppo_step0` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3297 | 0.1787 | 0.1584 | 1.5186 | 0.0000 | 0.0000 | 0.1810 | 0.0151 | 11 | 0.0206 | 22.5333 | 77.4667 | 13 | 0.9231 |
| `ppo_step0` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0283 | 0.3541 | 0.1879 | 0.1583 | 1.5243 | 0.0000 | 0.0000 | 0.1827 | 0.0175 | 12 | 0.0107 | 22.5333 | 77.4667 | 12 | 0.9167 |
| `ppo_step0` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 625 | `fall_or_nan` | 0.0010 | 0.0122 | 0.1858 | 0.0819 | 1.5172 | 0.0000 | 0.0000 | 0.1755 | 0.0321 | 14 | 0.0268 | 24.4800 | 75.0400 | 11 | 0.9091 |
| `ppo_step0` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0233 | 0.2911 | 0.1739 | 0.1578 | 1.5194 | 0.0000 | 0.0000 | 0.1792 | 0.0159 | 12 | 0.0194 | 23.0667 | 76.9333 | 13 | 0.9231 |
| `ppo_step0` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0282 | 0.3520 | 0.1668 | 0.1591 | 1.5188 | 0.0000 | 0.0000 | 0.1824 | 0.0147 | 14 | 0.0163 | 24.8000 | 75.2000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0` | 8 | 1 | 7 | 734.3750 | 625 | 750 | 0.2972 | 0.0238 | 0.1771 | 0.1490 | 0.0000 | 0.0000 | 0.0178 | 13.7500 | 0.0189 | 24.0767 | 75.8633 | 12.1250 | 0.9168 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
