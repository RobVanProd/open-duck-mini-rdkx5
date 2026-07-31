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
| `iter8_neighbor_stabilized_rate150` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0177 | 0.2214 | 0.1936 | 0.1527 | 1.5750 | 0.0000 | 0.0000 | 0.1686 | 0.0164 | 5 | 0.0084 | 14.8000 | 85.2000 | 12 | 0.9167 |
| `iter8_neighbor_stabilized_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 315 | `fall_or_nan` | 0.0819 | 1.0235 | 0.5011 | -0.0007 | 1.5648 | 0.0000 | 0.9262 | 0.1645 | 0.0581 | 6 | 0.0139 | 21.5873 | 77.7778 | 5 | 0.8000 |
| `iter8_neighbor_stabilized_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 229 | `fall_or_nan` | 0.0943 | 1.1787 | 0.6886 | -0.0129 | 1.4402 | 0.0000 | 0.3896 | 0.1669 | 0.0608 | 1 | 0.0060 | 11.7904 | 87.3362 | 4 | 0.5000 |
| `iter8_neighbor_stabilized_rate150` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 708 | `fall_or_nan` | 0.0371 | 0.4640 | 0.2853 | 0.0078 | 1.5358 | 0.0000 | 0.8892 | 0.1675 | 0.0599 | 3 | 0.0044 | 10.7345 | 89.1243 | 13 | 0.8462 |
| `iter8_neighbor_stabilized_rate150` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 638 | `fall_or_nan` | -0.0160 | -0.2001 | 0.1204 | 0.0850 | 1.5857 | 0.0000 | 0.0000 | 0.1525 | 0.0291 | 2 | 0.0009 | 8.1505 | 91.6928 | 11 | 0.8182 |
| `iter8_neighbor_stabilized_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 46 | `fall_or_nan` | -0.3058 | -3.8220 | 0.0522 | 0.0795 | 2.1293 | 0.0000 | 0.1800 | 0.2275 | 0.0242 | 1 | 0.0061 | 10.8696 | 84.7826 | 0 | NA |
| `iter8_neighbor_stabilized_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 300 | `fall_or_nan` | -0.0439 | -0.5482 | 0.0925 | 0.0781 | 1.6380 | 0.0000 | 0.1622 | 0.1720 | 0.0292 | 1 | 0.0170 | 14.0000 | 86.0000 | 5 | 0.8000 |
| `iter8_neighbor_stabilized_rate150` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0131 | 0.1635 | 0.1056 | 0.1568 | 1.5397 | 0.0000 | 0.0000 | 0.1596 | 0.0115 | 6 | 0.0074 | 12.4000 | 87.6000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter8_neighbor_stabilized_rate150` | 8 | 6 | 2 | 467.0000 | 46 | 750 | -0.1899 | -0.0152 | 0.2549 | 0.0683 | 0.0000 | 0.3184 | 0.0361 | 3.1250 | 0.0080 | 13.0415 | 86.1892 | 7.5000 | 0.7973 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
