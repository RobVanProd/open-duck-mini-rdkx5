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
| `phase2_z0075_iter1_rate150` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3278 | 0.1528 | 0.1528 | 1.5060 | 0.0000 | 0.0000 | 0.1757 | 0.0167 | 8 | 0.0179 | 21.4667 | 78.5333 | 12 | 0.9167 |
| `phase2_z0075_iter1_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 560 | `fall_or_nan` | 0.0617 | 0.7718 | 0.3217 | -0.0135 | 1.5313 | 0.0000 | 0.0000 | 0.1789 | 0.0589 | 14 | 0.0069 | 26.4286 | 73.0357 | 10 | 0.8000 |
| `phase2_z0075_iter1_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 643 | `fall_or_nan` | 0.0439 | 0.5482 | 0.2792 | 0.0025 | 1.5330 | 0.0000 | 1.9168 | 0.1834 | 0.0604 | 10 | 0.0111 | 16.0187 | 83.6703 | 11 | 0.9091 |
| `phase2_z0075_iter1_rate150` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 85 | `fall_or_nan` | -0.2159 | -2.6989 | 0.1622 | 0.0708 | 2.0590 | 0.0000 | 2.3114 | 0.1575 | 0.0349 | 1 | 0.0060 | 10.5882 | 87.0588 | 1 | 0.0000 |
| `phase2_z0075_iter1_rate150` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 478 | `fall_or_nan` | 0.0569 | 0.7113 | 0.3303 | -0.0115 | 1.4998 | 0.0000 | 0.1771 | 0.1692 | 0.0578 | 4 | 0.0072 | 14.2259 | 85.3556 | 8 | 0.8750 |
| `phase2_z0075_iter1_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.2883 | -3.6031 | 0.0359 | 0.0875 | 3.4897 | 1.4589 | 3.2400 | 0.3202 | 0.0290 | 2 | 0.0085 | 6.2500 | 85.4167 | 0 | NA |
| `phase2_z0075_iter1_rate150` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0180 | 0.2247 | 0.1110 | 0.1533 | 1.5177 | 0.0000 | 0.8566 | 0.1785 | 0.0126 | 7 | 0.0094 | 16.4000 | 83.6000 | 13 | 0.9231 |
| `phase2_z0075_iter1_rate150` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0274 | 0.3420 | 0.1456 | 0.1568 | 1.5154 | 0.0000 | 0.0000 | 0.1789 | 0.0175 | 18 | 0.0184 | 23.6000 | 76.4000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase2_z0075_iter1_rate150` | 8 | 5 | 3 | 508.0000 | 48 | 750 | -0.4221 | -0.0338 | 0.1923 | 0.0748 | 0.1824 | 1.0627 | 0.0360 | 8.0000 | 0.0107 | 16.8723 | 81.6338 | 8.1250 | 0.7605 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
