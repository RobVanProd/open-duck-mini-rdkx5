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
| `smooth` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0344 | 0.4300 | 0.1021 | 0.1519 | 2.3758 | 0.0000 | 0.1953 | 0.0120 | 5 | 0.0101 | 23.6000 | 76.4000 | 4 | 0.7500 |
| `smooth` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0327 | 0.4086 | 0.1285 | 0.1563 | 2.3859 | 0.0000 | 0.1974 | 0.0120 | 4 | 0.0192 | 27.2000 | 72.4000 | 4 | 1.0000 |
| `smooth` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0394 | 0.4920 | 0.1191 | 0.1511 | 2.3310 | 0.0000 | 0.1960 | 0.0123 | 5 | 0.0103 | 29.2000 | 70.8000 | 4 | 0.7500 |
| `smooth` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0258 | 0.3230 | 0.1234 | 0.1548 | 2.3923 | 0.0000 | 0.1897 | 0.0112 | 4 | 0.0039 | 22.4000 | 77.6000 | 4 | 1.0000 |
| `smooth` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0371 | 0.4636 | 0.1105 | 0.1507 | 2.4339 | 0.0000 | 0.1960 | 0.0112 | 4 | 0.0147 | 24.0000 | 76.0000 | 4 | 0.7500 |
| `smooth` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0359 | 0.4487 | 0.1037 | 0.1464 | 2.3549 | 0.0000 | 0.1958 | 0.0184 | 5 | 0.0076 | 19.6000 | 79.6000 | 4 | 1.0000 |
| `smooth` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0360 | 0.4502 | 0.1159 | 0.1531 | 2.3786 | 0.0000 | 0.1983 | 0.0170 | 8 | 0.0074 | 28.0000 | 72.0000 | 4 | 1.0000 |
| `smooth` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0337 | 0.4218 | 0.1087 | 0.1565 | 2.4623 | 0.0000 | 0.1986 | 0.0121 | 3 | 0.0130 | 23.6000 | 76.4000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `smooth` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4297 | 0.0344 | 0.1140 | 0.1526 | 0.0000 | 0.0133 | 4.7500 | 0.0108 | 24.7000 | 75.1500 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
