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
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0026`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `tc81920` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0324 | 0.4054 | 0.1438 | 0.1519 | 1.7701 | 0.0000 | 0.0000 | 0.1976 | 0.0161 | 12 | 0.0181 | 23.3333 | 76.6667 | 0 | NA |
| `tc81920` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0350 | 0.4371 | 0.1410 | 0.1563 | 1.7889 | 0.0000 | 0.0000 | 0.1983 | 0.0123 | 20 | 0.0099 | 25.8667 | 74.0000 | 0 | NA |
| `tc81920` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0337 | 0.4216 | 0.1435 | 0.1511 | 1.7911 | 0.0000 | 0.0000 | 0.1990 | 0.0159 | 18 | 0.0178 | 25.8667 | 74.1333 | 0 | NA |
| `tc81920` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0313 | 0.3916 | 0.1359 | 0.1556 | 1.7894 | 0.0000 | 0.0000 | 0.1950 | 0.0110 | 15 | 0.0060 | 24.4000 | 75.6000 | 0 | NA |
| `tc81920` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0317 | 0.3967 | 0.1339 | 0.1507 | 1.7931 | 0.0000 | 0.0000 | 0.1964 | 0.0120 | 16 | 0.0081 | 22.2667 | 77.7333 | 0 | NA |
| `tc81920` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | `fall_or_nan` | -0.2279 | -2.8483 | 0.0826 | 0.0667 | 1.8401 | 0.0000 | 0.0000 | 0.2022 | 0.0331 | 2 | 0.0083 | 9.2308 | 83.0769 | 0 | NA |
| `tc81920` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0351 | 0.4388 | 0.1325 | 0.1531 | 1.7971 | 0.0000 | 0.0000 | 0.1980 | 0.0137 | 17 | 0.0125 | 27.3333 | 72.6667 | 0 | NA |
| `tc81920` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0342 | 0.4271 | 0.1341 | 0.1564 | 1.7877 | 0.0000 | 0.0000 | 0.1987 | 0.0114 | 20 | 0.0090 | 26.5333 | 73.4667 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `tc81920` | 8 | 1 | 7 | 664.3750 | 65 | 750 | 0.0087 | 0.0007 | 0.1309 | 0.1427 | 0.0000 | 0.0000 | 0.0157 | 15.0000 | 0.0112 | 23.1038 | 75.9179 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
