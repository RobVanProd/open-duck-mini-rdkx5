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
| `smooth` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0342 | 0.4279 | 0.1047 | 0.1519 | 2.3349 | 0.0000 | 0.1951 | 0.0116 | 4 | 0.0083 | 24.0000 | 76.0000 | 4 | 0.7500 |
| `smooth` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0343 | 0.4286 | 0.1288 | 0.1563 | 2.3783 | 0.0000 | 0.1963 | 0.0133 | 4 | 0.0192 | 28.8000 | 70.8000 | 4 | 1.0000 |
| `smooth` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0408 | 0.5098 | 0.1113 | 0.1511 | 2.3242 | 0.0000 | 0.1965 | 0.0124 | 7 | 0.0093 | 29.6000 | 70.4000 | 4 | 0.7500 |
| `smooth` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0258 | 0.3231 | 0.1276 | 0.1548 | 2.4252 | 0.0000 | 0.1884 | 0.0115 | 5 | 0.0046 | 22.8000 | 77.2000 | 4 | 1.0000 |
| `smooth` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0373 | 0.4657 | 0.1100 | 0.1507 | 2.4035 | 0.0000 | 0.1967 | 0.0111 | 3 | 0.0045 | 22.4000 | 77.6000 | 4 | 0.7500 |
| `smooth` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0320 | 0.4006 | 0.1087 | 0.1464 | 2.4097 | 0.0000 | 0.1946 | 0.0185 | 5 | 0.0076 | 15.2000 | 84.0000 | 4 | 1.0000 |
| `smooth` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0340 | 0.4245 | 0.1166 | 0.1531 | 2.4068 | 0.0000 | 0.1949 | 0.0171 | 6 | 0.0075 | 27.2000 | 72.8000 | 4 | 1.0000 |
| `smooth` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0309 | 0.3856 | 0.0997 | 0.1565 | 2.3553 | 0.0000 | 0.1981 | 0.0118 | 4 | 0.0086 | 24.0000 | 76.0000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `smooth` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4207 | 0.0337 | 0.1134 | 0.1526 | 0.0000 | 0.0134 | 4.7500 | 0.0087 | 24.2500 | 75.6000 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
