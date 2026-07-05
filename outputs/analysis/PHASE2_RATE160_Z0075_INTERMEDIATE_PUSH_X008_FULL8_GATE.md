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
| `phase_mod_rate160` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0287 | 0.3587 | 0.1845 | 0.1579 | 1.6493 | 0.0000 | 0.0772 | 0.1869 | 0.0179 | 13 | 0.0221 | 24.4000 | 75.6000 | 12 | 0.9167 |
| `phase_mod_rate160` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0269 | 0.3364 | 0.1799 | 0.1564 | 1.6456 | 0.0000 | 0.0772 | 0.1935 | 0.0142 | 15 | 0.0192 | 23.6000 | 76.4000 | 13 | 1.0000 |
| `phase_mod_rate160` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0300 | 0.3754 | 0.1766 | 0.1579 | 1.6499 | 0.0000 | 0.0772 | 0.1907 | 0.0156 | 17 | 0.0258 | 26.6667 | 73.3333 | 13 | 0.9231 |
| `phase_mod_rate160` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0172 | 0.2148 | 0.1699 | 0.1579 | 1.5597 | 0.0000 | 0.0772 | 0.1622 | 0.0167 | 9 | 0.0227 | 15.0667 | 84.9333 | 13 | 1.0000 |
| `phase_mod_rate160` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0256 | 0.3205 | 0.1795 | 0.1579 | 1.6429 | 0.0000 | 0.1379 | 0.1851 | 0.0159 | 11 | 0.0200 | 22.6667 | 77.3333 | 12 | 1.0000 |
| `phase_mod_rate160` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0282 | 0.3530 | 0.1777 | 0.1577 | 1.6503 | 0.0000 | 0.0772 | 0.1878 | 0.0154 | 13 | 0.0250 | 23.3333 | 76.6667 | 13 | 1.0000 |
| `phase_mod_rate160` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0232 | 0.2906 | 0.1834 | 0.1579 | 1.6715 | 0.0000 | 0.0772 | 0.1859 | 0.0157 | 9 | 0.0193 | 20.6667 | 79.3333 | 13 | 0.9231 |
| `phase_mod_rate160` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0260 | 0.3250 | 0.1996 | 0.1570 | 1.6414 | 0.0000 | 0.0772 | 0.1863 | 0.0201 | 13 | 0.0164 | 24.4000 | 75.6000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate160` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3218 | 0.0257 | 0.1814 | 0.1576 | 0.0000 | 0.0847 | 0.0164 | 12.5000 | 0.0213 | 22.6000 | 77.4000 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
