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
| `iter1bp_15360` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0014 | 0.0174 | 0.0550 | 0.1626 | 0.2661 | 0.0000 | 0.1017 | 0.0459 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `iter1bp_15360` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0014 | 0.0178 | 0.0573 | 0.1619 | 0.2682 | 0.0000 | 0.1017 | 0.0472 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `iter1bp_15360` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0014 | 0.0179 | 0.0555 | 0.1625 | 0.2699 | 0.0000 | 0.1017 | 0.0479 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter1bp_15360` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0014 | 0.0178 | 0.0591 | 0.1622 | 0.2563 | 0.0000 | 0.1017 | 0.0476 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter1bp_15360` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0014 | 0.0181 | 0.0537 | 0.1624 | 0.2714 | 0.0000 | 0.1017 | 0.0464 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |
| `iter1bp_30720` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0192 | 0.0603 | 0.1624 | 0.1559 | 0.0000 | 0.0000 | 0.0471 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `iter1bp_30720` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0195 | 0.0631 | 0.1619 | 0.1524 | 0.0000 | 0.0000 | 0.0472 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `iter1bp_30720` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0196 | 0.0641 | 0.1624 | 0.1551 | 0.0000 | 0.0000 | 0.0471 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter1bp_30720` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0197 | 0.0641 | 0.1623 | 0.1519 | 0.0000 | 0.0000 | 0.0476 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter1bp_30720` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0188 | 0.0632 | 0.1621 | 0.1435 | 0.0000 | 0.0000 | 0.0466 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |
| `iter1bp_46080` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0191 | 0.0650 | 0.1626 | 0.1672 | 0.0000 | 0.0000 | 0.0491 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `iter1bp_46080` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0192 | 0.0687 | 0.1620 | 0.1581 | 0.0000 | 0.0000 | 0.0499 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `iter1bp_46080` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0195 | 0.0688 | 0.1626 | 0.1735 | 0.0000 | 0.0000 | 0.0495 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter1bp_46080` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0197 | 0.0695 | 0.1624 | 0.1735 | 0.0000 | 0.0000 | 0.0503 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter1bp_46080` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0186 | 0.0685 | 0.1623 | 0.1637 | 0.0000 | 0.0000 | 0.0489 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter1bp_15360` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.0178 | 0.0014 | 0.0561 | 0.1623 | 0.0000 | 0.1017 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.2000 | 0.9526 |
| `iter1bp_30720` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.0193 | 0.0015 | 0.0630 | 0.1622 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.2000 | 0.9526 |
| `iter1bp_46080` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.0192 | 0.0015 | 0.0681 | 0.1624 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.2000 | 0.9526 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
