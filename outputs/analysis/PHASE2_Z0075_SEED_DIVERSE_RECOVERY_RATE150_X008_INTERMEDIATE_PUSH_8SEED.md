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
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter7_seed_diverse_recovery_rate150` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0298 | 0.3720 | 0.1623 | 0.1527 | 1.5443 | 0.0000 | 0.0000 | 0.1852 | 0.0172 | 11 | 0.0257 | 25.2000 | 74.8000 | 12 | 0.9167 |
| `iter7_seed_diverse_recovery_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 513 | `fall_or_nan` | 0.0651 | 0.8139 | 0.3064 | 0.0098 | 1.5384 | 0.0000 | 0.0000 | 0.1860 | 0.0618 | 12 | 0.0115 | 29.8246 | 69.5906 | 9 | 0.8889 |
| `iter7_seed_diverse_recovery_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 155 | `fall_or_nan` | 0.1368 | 1.7105 | 0.8375 | 0.0018 | 1.5446 | 0.0000 | 0.0000 | 0.2035 | 0.0604 | 3 | 0.0054 | 20.6452 | 77.4194 | 2 | 0.5000 |
| `iter7_seed_diverse_recovery_rate150` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 129 | `fall_or_nan` | -0.1462 | -1.8271 | 0.1345 | 0.0696 | 1.6201 | 0.0000 | 0.2339 | 0.1757 | 0.0336 | 0 | 0.0000 | 4.6512 | 94.5736 | 2 | 0.5000 |
| `iter7_seed_diverse_recovery_rate150` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 422 | `fall_or_nan` | 0.0622 | 0.7771 | 0.3959 | 0.0126 | 1.5477 | 0.0000 | 0.0000 | 0.1827 | 0.0573 | 4 | 0.0072 | 18.7204 | 81.2796 | 7 | 0.8571 |
| `iter7_seed_diverse_recovery_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -0.3200 | -4.0006 | 0.0556 | 0.0633 | 1.6927 | 0.0000 | 0.0000 | 0.2190 | 0.0288 | 1 | 0.0040 | 21.2766 | 74.4681 | 0 | NA |
| `iter7_seed_diverse_recovery_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 430 | `fall_or_nan` | 0.0687 | 0.8593 | 0.3797 | -0.0028 | 1.5356 | 0.0000 | 0.0000 | 0.1856 | 0.0612 | 9 | 0.0224 | 24.1860 | 75.1163 | 7 | 0.8571 |
| `iter7_seed_diverse_recovery_rate150` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 617 | `fall_or_nan` | 0.0541 | 0.6758 | 0.2610 | 0.0067 | 1.5461 | 0.0000 | 0.0000 | 0.1851 | 0.0601 | 16 | 0.0169 | 25.1216 | 74.5543 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter7_seed_diverse_recovery_rate150` | 8 | 7 | 1 | 382.8750 | 47 | 750 | -0.0774 | -0.0062 | 0.3166 | 0.0392 | 0.0000 | 0.0292 | 0.0476 | 7.0000 | 0.0116 | 21.2032 | 77.7252 | 5.8750 | 0.7707 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
