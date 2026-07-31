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
| `iter21_seed5_postpush` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0330 | 0.4129 | 0.1824 | 0.1595 | 1.6669 | 0.0000 | 0.0000 | 0.1868 | 0.0181 | 14 | 0.0273 | 27.4667 | 72.5333 | 12 | 0.9167 |
| `iter21_seed5_postpush` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0327 | 0.4093 | 0.1809 | 0.1587 | 1.6512 | 0.0000 | 0.0000 | 0.1875 | 0.0166 | 17 | 0.0288 | 28.4000 | 71.6000 | 13 | 0.9231 |
| `iter21_seed5_postpush` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 455 | `fall_or_nan` | 0.0707 | 0.8843 | 0.3731 | -0.0068 | 1.6276 | 0.0000 | 0.0000 | 0.1842 | 0.0604 | 10 | 0.0272 | 26.3736 | 73.4066 | 7 | 0.8571 |
| `iter21_seed5_postpush` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 491 | `fall_or_nan` | -0.0060 | -0.0747 | 0.1845 | 0.0725 | 1.6478 | 0.0000 | 0.0000 | 0.1856 | 0.0321 | 11 | 0.0236 | 25.4582 | 74.1344 | 9 | 0.7778 |
| `iter21_seed5_postpush` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0273 | 0.3418 | 0.1731 | 0.1597 | 1.6464 | 0.0000 | 0.0000 | 0.1876 | 0.0150 | 10 | 0.0257 | 23.7333 | 76.2667 | 12 | 0.9167 |
| `iter21_seed5_postpush` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0372 | 0.4644 | 0.2009 | 0.1581 | 1.6664 | 0.0000 | 0.0000 | 0.1896 | 0.0181 | 15 | 0.0290 | 27.7333 | 72.2667 | 13 | 0.9231 |
| `iter21_seed5_postpush` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 180 | `fall_or_nan` | 0.1254 | 1.5672 | 0.7792 | 0.0043 | 1.5527 | 0.0000 | 0.0000 | 0.1935 | 0.0584 | 3 | 0.0114 | 17.2222 | 82.2222 | 3 | 0.3333 |
| `iter21_seed5_postpush` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0334 | 0.4170 | 0.1857 | 0.1592 | 1.6490 | 0.0000 | 0.0000 | 0.1916 | 0.0152 | 18 | 0.0291 | 28.9333 | 71.0667 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_seed5_postpush` | 8 | 3 | 5 | 609.5000 | 180 | 750 | 0.5528 | 0.0442 | 0.2825 | 0.1081 | 0.0000 | 0.0000 | 0.0292 | 12.2500 | 0.0253 | 25.6651 | 74.1871 | 9.8750 | 0.8185 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
