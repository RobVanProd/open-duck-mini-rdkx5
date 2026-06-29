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
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0g_20480` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0387 | 0.4832 | 0.1439 | 0.1519 | 1.7513 | 0.0000 | 0.2031 | 0.0154 | 5 | 0.0144 | 25.6000 | 74.4000 | 4 | 0.7500 |
| `b0g_20480` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0331 | 0.4143 | 0.1337 | 0.1562 | 1.7946 | 0.0000 | 0.1985 | 0.0130 | 8 | 0.0043 | 25.6000 | 74.0000 | 4 | 1.0000 |
| `b0g_20480` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0390 | 0.4874 | 0.1443 | 0.1511 | 1.7637 | 0.0000 | 0.2036 | 0.0153 | 8 | 0.0154 | 29.6000 | 70.4000 | 4 | 0.7500 |
| `b0g_20480` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0263 | 0.3283 | 0.1451 | 0.1552 | 1.7650 | 0.0000 | 0.1985 | 0.0119 | 5 | 0.0066 | 23.2000 | 76.8000 | 4 | 1.0000 |
| `b0g_20480` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0360 | 0.4504 | 0.1434 | 0.1506 | 1.8094 | 0.0000 | 0.2013 | 0.0122 | 4 | 0.0091 | 17.6000 | 82.4000 | 4 | 0.7500 |
| `b0g_20480` | 5 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0377 | 0.4707 | 0.1330 | 0.1462 | 1.7965 | 0.0000 | 0.2046 | 0.0184 | 6 | 0.0085 | 18.0000 | 81.2000 | 4 | 1.0000 |
| `b0g_20480` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0372 | 0.4644 | 0.1340 | 0.1530 | 1.7879 | 0.0000 | 0.1999 | 0.0147 | 6 | 0.0137 | 28.4000 | 71.6000 | 4 | 1.0000 |
| `b0g_20480` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0352 | 0.4396 | 0.1282 | 0.1564 | 1.7653 | 0.0000 | 0.1993 | 0.0107 | 6 | 0.0094 | 25.2000 | 74.8000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0g_20480` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4423 | 0.0354 | 0.1382 | 0.1526 | 0.0000 | 0.0140 | 6.0000 | 0.0102 | 24.1500 | 75.7000 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
