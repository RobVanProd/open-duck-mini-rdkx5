# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0371 | 0.4632 | 0.1456 | 0.1519 | 1.7824 | 0.0000 | 0.2034 | 0.0155 | 6 | 0.0099 | 20.8000 | 79.2000 | 4 | 0.7500 |
| `b0` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0309 | 0.3859 | 0.1438 | 0.1562 | 1.7719 | 0.0000 | 0.1967 | 0.0126 | 6 | 0.0111 | 26.8000 | 72.8000 | 4 | 1.0000 |
| `b0` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0337 | 0.4207 | 0.1364 | 0.1511 | 1.7941 | 0.0000 | 0.2007 | 0.0142 | 6 | 0.0061 | 26.8000 | 73.2000 | 4 | 0.7500 |
| `b0` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0252 | 0.3154 | 0.1486 | 0.1548 | 1.7293 | 0.0000 | 0.1936 | 0.0119 | 5 | 0.0061 | 20.8000 | 79.2000 | 4 | 1.0000 |
| `b0` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0343 | 0.4291 | 0.1385 | 0.1506 | 1.7980 | 0.0000 | 0.2027 | 0.0117 | 4 | 0.0114 | 16.8000 | 83.2000 | 4 | 0.7500 |
| `b0` | 5 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0393 | 0.4918 | 0.1495 | 0.1462 | 1.7712 | 0.0000 | 0.2050 | 0.0184 | 5 | 0.0092 | 20.0000 | 79.2000 | 4 | 1.0000 |
| `b0` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0394 | 0.4930 | 0.1436 | 0.1530 | 1.7457 | 0.0000 | 0.1992 | 0.0145 | 6 | 0.0135 | 27.6000 | 72.4000 | 4 | 1.0000 |
| `b0` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0356 | 0.4455 | 0.1277 | 0.1564 | 1.7892 | 0.0000 | 0.1997 | 0.0108 | 5 | 0.0168 | 24.8000 | 75.2000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4306 | 0.0344 | 0.1417 | 0.1525 | 0.0000 | 0.0137 | 5.3750 | 0.0105 | 23.0500 | 76.8000 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
