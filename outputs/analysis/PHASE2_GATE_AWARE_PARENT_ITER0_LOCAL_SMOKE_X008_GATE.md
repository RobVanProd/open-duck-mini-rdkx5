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
| `iter0_15360` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0182 | 0.0580 | 0.1624 | 0.3349 | 0.0000 | 0.1717 | 0.0523 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `iter0_15360` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0184 | 0.0588 | 0.1618 | 0.3364 | 0.0000 | 0.1717 | 0.0552 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `iter0_15360` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0189 | 0.0587 | 0.1624 | 0.3349 | 0.0000 | 0.1717 | 0.0529 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter0_15360` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0189 | 0.0623 | 0.1621 | 0.3349 | 0.0000 | 0.1717 | 0.0527 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter0_15360` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0184 | 0.0574 | 0.1623 | 0.3349 | 0.0000 | 0.1717 | 0.0497 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |
| `iter0_30720` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0192 | 0.0591 | 0.1625 | 0.1643 | 0.0000 | 0.0000 | 0.0482 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `iter0_30720` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0194 | 0.0622 | 0.1620 | 0.1625 | 0.0000 | 0.0000 | 0.0482 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `iter0_30720` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0194 | 0.0635 | 0.1625 | 0.1638 | 0.0000 | 0.0000 | 0.0482 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter0_30720` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0198 | 0.0629 | 0.1624 | 0.1625 | 0.0000 | 0.0000 | 0.0487 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter0_30720` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0187 | 0.0624 | 0.1622 | 0.1553 | 0.0000 | 0.0000 | 0.0476 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |
| `iter0_46080` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0192 | 0.0662 | 0.1626 | 0.1891 | 0.0000 | 0.0000 | 0.0512 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `iter0_46080` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0196 | 0.0691 | 0.1621 | 0.1830 | 0.0000 | 0.0000 | 0.0516 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `iter0_46080` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0195 | 0.0694 | 0.1627 | 0.1938 | 0.0000 | 0.0000 | 0.0514 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter0_46080` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0016 | 0.0198 | 0.0689 | 0.1626 | 0.1890 | 0.0000 | 0.0000 | 0.0522 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `iter0_46080` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0188 | 0.0688 | 0.1624 | 0.1862 | 0.0000 | 0.0000 | 0.0509 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter0_15360` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.0186 | 0.0015 | 0.0590 | 0.1622 | 0.0000 | 0.1717 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.2000 | 0.9526 |
| `iter0_30720` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.0193 | 0.0015 | 0.0620 | 0.1623 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.2000 | 0.9526 |
| `iter0_46080` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.0194 | 0.0016 | 0.0685 | 0.1625 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.2000 | 0.9526 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
