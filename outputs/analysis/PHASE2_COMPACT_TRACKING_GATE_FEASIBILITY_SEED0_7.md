# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `1.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `None`
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
| `bounded_teacher` | 0 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0390 | 0.4870 | 0.1069 | 0.1520 | 1.8166 | 0.0000 | 0.0000 | 0.2478 | 0.0082 | 1 | 0.0032 | 20.0000 | 80.0000 | 0 | NA |
| `bounded_teacher` | 1 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0305 | 0.3819 | 0.1044 | 0.1556 | 1.8035 | 0.0000 | 0.0000 | 0.2043 | 0.0111 | 2 | 0.0034 | 36.0000 | 62.0000 | 0 | NA |
| `bounded_teacher` | 2 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0471 | 0.5885 | 0.0786 | 0.1509 | 1.7419 | 0.0000 | 0.0000 | 0.2479 | 0.0057 | 2 | 0.0024 | 30.0000 | 70.0000 | 0 | NA |
| `bounded_teacher` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0426 | -0.5326 | 0.2301 | 0.1551 | 1.8078 | 0.0000 | 0.0000 | 0.1840 | 0.0134 | 1 | 0.0025 | 26.0000 | 70.0000 | 0 | NA |
| `bounded_teacher` | 4 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0502 | 0.6279 | 0.0562 | 0.1506 | 1.8385 | 0.0000 | 0.0000 | 0.1716 | 0.0060 | 1 | 0.0002 | 14.0000 | 86.0000 | 0 | NA |
| `bounded_teacher` | 5 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0547 | 0.6834 | 0.0330 | 0.1462 | 2.0000 | 0.0000 | 0.0000 | 0.2414 | 0.0183 | 1 | 0.0036 | 8.0000 | 88.0000 | 0 | NA |
| `bounded_teacher` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0042 | 0.0521 | 0.0522 | 0.1557 | 1.7756 | 0.0000 | 0.0000 | 0.1851 | 0.0154 | 1 | 0.0071 | 34.0000 | 66.0000 | 0 | NA |
| `bounded_teacher` | 7 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0368 | 0.4603 | 0.1078 | 0.1559 | 1.8133 | 0.0000 | 0.0000 | 0.2210 | 0.0111 | 1 | 0.0039 | 38.0000 | 62.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `bounded_teacher` | 8 | 0 | 8 | 50.0000 | 50 | 50 | 0.3436 | 0.0275 | 0.0962 | 0.1528 | 0.0000 | 0.0000 | 0.0112 | 1.2500 | 0.0033 | 25.7500 | 73.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
