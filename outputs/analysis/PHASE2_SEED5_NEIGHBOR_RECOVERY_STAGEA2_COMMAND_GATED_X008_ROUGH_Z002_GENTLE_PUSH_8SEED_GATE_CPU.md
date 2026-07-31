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
| `gated` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0353 | 0.4411 | 0.0990 | 0.1519 | 2.4244 | 0.0000 | 0.1940 | 0.0123 | 5 | 0.0103 | 23.6000 | 76.4000 | 4 | 0.7500 |
| `gated` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0316 | 0.3952 | 0.1241 | 0.1563 | 2.3350 | 0.0000 | 0.1963 | 0.0121 | 4 | 0.0193 | 28.0000 | 71.6000 | 4 | 1.0000 |
| `gated` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0409 | 0.5111 | 0.1121 | 0.1511 | 2.3822 | 0.0000 | 0.1964 | 0.0122 | 8 | 0.0084 | 29.6000 | 70.4000 | 4 | 0.7500 |
| `gated` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0253 | 0.3159 | 0.1300 | 0.1548 | 2.3606 | 0.0000 | 0.1914 | 0.0118 | 4 | 0.0054 | 21.2000 | 78.8000 | 4 | 1.0000 |
| `gated` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0370 | 0.4620 | 0.1107 | 0.1507 | 2.3406 | 0.0000 | 0.1945 | 0.0110 | 4 | 0.0072 | 22.8000 | 77.2000 | 4 | 0.7500 |
| `gated` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0356 | 0.4453 | 0.1099 | 0.1464 | 2.3282 | 0.0000 | 0.1955 | 0.0185 | 5 | 0.0076 | 18.4000 | 80.8000 | 4 | 1.0000 |
| `gated` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 250 | `duration_complete` | 0.0340 | 0.4246 | 0.1073 | 0.1531 | 2.4392 | 0.0212 | 0.1942 | 0.0170 | 7 | 0.0083 | 26.8000 | 73.2000 | 4 | 1.0000 |
| `gated` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0333 | 0.4165 | 0.1026 | 0.1565 | 2.3370 | 0.0000 | 0.1950 | 0.0105 | 4 | 0.0143 | 25.2000 | 74.8000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4264 | 0.0341 | 0.1120 | 0.1526 | 0.0026 | 0.0132 | 5.1250 | 0.0101 | 24.4500 | 75.4000 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
