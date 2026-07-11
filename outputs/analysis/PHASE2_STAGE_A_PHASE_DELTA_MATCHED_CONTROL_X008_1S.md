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
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `matched_control` | 0 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0346 | 0.4326 | 0.0998 | 0.1520 | 1.6573 | 0.0000 | 0.0000 | 0.2384 | 0.0070 | 0 | 0.0000 | 16.0000 | 84.0000 | 0 | NA |
| `matched_control` | 1 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0257 | 0.3214 | 0.1095 | 0.1556 | 1.7232 | 0.0000 | 0.0000 | 0.2165 | 0.0026 | 1 | 0.0069 | 28.0000 | 70.0000 | 0 | NA |
| `matched_control` | 2 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0517 | 0.6466 | 0.0988 | 0.1509 | 1.6610 | 0.0000 | 0.0000 | 0.2345 | 0.0095 | 3 | 0.0057 | 40.0000 | 60.0000 | 0 | NA |
| `matched_control` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0455 | -0.5686 | 0.2270 | 0.1555 | 1.5973 | 0.0000 | 0.0000 | 0.1798 | 0.0134 | 1 | 0.0016 | 18.0000 | 78.0000 | 0 | NA |
| `matched_control` | 4 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0544 | 0.6795 | 0.0849 | 0.1506 | 1.7472 | 0.0000 | 0.0000 | 0.1774 | 0.0030 | 0 | 0.0000 | 10.0000 | 90.0000 | 0 | NA |
| `matched_control` | 5 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0583 | 0.7285 | 0.0129 | 0.1462 | 1.6500 | 0.0000 | 0.0000 | 0.2356 | 0.0189 | 1 | 0.0036 | 6.0000 | 90.0000 | 0 | NA |
| `matched_control` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0114 | 0.1422 | 0.0882 | 0.1557 | 1.5671 | 0.0000 | 0.0000 | 0.1947 | 0.0156 | 2 | 0.0109 | 44.0000 | 56.0000 | 0 | NA |
| `matched_control` | 7 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0358 | 0.4474 | 0.1012 | 0.1559 | 1.5753 | 0.0000 | 0.0000 | 0.2170 | 0.0103 | 1 | 0.0051 | 36.0000 | 64.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `matched_control` | 8 | 0 | 8 | 50.0000 | 50 | 50 | 0.3537 | 0.0283 | 0.1028 | 0.1528 | 0.0000 | 0.0000 | 0.0101 | 1.1250 | 0.0042 | 24.7500 | 74.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
