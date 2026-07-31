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
| `lk097` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0365 | 0.4564 | 0.1428 | 0.1519 | 1.7650 | 0.0000 | 0.1990 | 0.0141 | 7 | 0.0037 | 24.4000 | 75.6000 | 4 | 0.7500 |
| `lk097` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0310 | 0.3881 | 0.1402 | 0.1562 | 1.7791 | 0.0000 | 0.1936 | 0.0119 | 6 | 0.0069 | 27.6000 | 72.0000 | 4 | 1.0000 |
| `lk097` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0371 | 0.4633 | 0.1334 | 0.1511 | 1.7963 | 0.0000 | 0.1973 | 0.0143 | 7 | 0.0062 | 26.4000 | 73.6000 | 4 | 0.7500 |
| `lk097` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0270 | 0.3381 | 0.1462 | 0.1551 | 1.7520 | 0.0000 | 0.1945 | 0.0121 | 5 | 0.0052 | 21.6000 | 78.4000 | 4 | 1.0000 |
| `lk097` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0343 | 0.4285 | 0.1402 | 0.1506 | 1.8002 | 0.0000 | 0.2013 | 0.0115 | 3 | 0.0113 | 17.6000 | 82.4000 | 4 | 0.7500 |
| `lk097` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0390 | 0.4874 | 0.1293 | 0.1462 | 1.7834 | 0.0000 | 0.1971 | 0.0184 | 5 | 0.0129 | 19.2000 | 80.0000 | 4 | 1.0000 |
| `lk097` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0388 | 0.4845 | 0.1331 | 0.1530 | 1.7845 | 0.0000 | 0.1953 | 0.0148 | 6 | 0.0136 | 27.6000 | 72.4000 | 4 | 1.0000 |
| `lk097` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0349 | 0.4363 | 0.1235 | 0.1564 | 1.7695 | 0.0000 | 0.1932 | 0.0107 | 7 | 0.0098 | 25.6000 | 74.4000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lk097` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4353 | 0.0348 | 0.1361 | 0.1526 | 0.0000 | 0.0135 | 5.7500 | 0.0087 | 23.7500 | 76.1000 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
