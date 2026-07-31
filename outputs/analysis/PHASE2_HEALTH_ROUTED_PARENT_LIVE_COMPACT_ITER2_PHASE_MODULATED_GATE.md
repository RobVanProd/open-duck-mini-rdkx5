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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_compact_phase_mod` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 675 | `fall_or_nan` | 0.0567 | 0.7081 | 0.2969 | -0.0065 | 1.5994 | 0.0000 | 0.0000 | 0.1818 | 0.0622 | 15 | 0.0193 | 27.1111 | 72.7407 | 11 | 0.9091 |
| `live_compact_phase_mod` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 471 | `fall_or_nan` | -0.0078 | -0.0977 | 0.1577 | 0.0702 | 1.6154 | 0.0000 | 0.0000 | 0.1752 | 0.0320 | 10 | 0.0210 | 24.6285 | 75.1592 | 8 | 0.8750 |
| `live_compact_phase_mod` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0305 | 0.3817 | 0.1774 | 0.1585 | 1.5991 | 0.0000 | 0.0000 | 0.1842 | 0.0166 | 17 | 0.0173 | 27.0667 | 72.9333 | 13 | 0.9231 |
| `live_compact_phase_mod` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0296 | 0.3695 | 0.1806 | 0.1587 | 1.5964 | 0.0000 | 0.0000 | 0.1841 | 0.0160 | 16 | 0.0276 | 24.5333 | 75.4667 | 13 | 0.9231 |
| `live_compact_phase_mod` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 296 | `fall_or_nan` | -0.0402 | -0.5019 | 0.1730 | 0.0695 | 1.6334 | 0.0000 | 0.0000 | 0.1750 | 0.0354 | 6 | 0.0120 | 20.6081 | 79.0541 | 4 | 0.7500 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_compact_phase_mod` | 5 | 3 | 2 | 588.4000 | 296 | 750 | 0.1719 | 0.0138 | 0.1971 | 0.0901 | 0.0000 | 0.0000 | 0.0324 | 12.8000 | 0.0194 | 24.7895 | 75.0708 | 9.8000 | 0.8760 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
