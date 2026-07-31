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
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
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
| `seed5_early` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0320 | 0.4001 | 0.1087 | 0.1519 | 2.4225 | 0.0000 | 0.2069 | 0.0117 | 6 | 0.0019 | 22.4000 | 77.6000 | 0 | NA |
| `seed5_early` | 1 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0333 | 0.4159 | 0.1191 | 0.1563 | 2.2839 | 0.0000 | 0.2031 | 0.0128 | 4 | 0.0117 | 26.0000 | 73.6000 | 0 | NA |
| `seed5_early` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0395 | 0.4934 | 0.1011 | 0.1511 | 2.3123 | 0.0000 | 0.1998 | 0.0108 | 8 | 0.0087 | 28.8000 | 71.2000 | 0 | NA |
| `seed5_early` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0291 | 0.3634 | 0.1318 | 0.1555 | 2.3866 | 0.0000 | 0.1946 | 0.0120 | 4 | 0.0042 | 24.0000 | 76.0000 | 0 | NA |
| `seed5_early` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0361 | 0.4512 | 0.1046 | 0.1506 | 2.3564 | 0.0000 | 0.1977 | 0.0108 | 4 | 0.0074 | 21.2000 | 78.8000 | 0 | NA |
| `seed5_early` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3300 | -4.1252 | 0.0613 | 0.0459 | 4.3076 | 1.8076 | 0.2281 | 0.0299 | 1 | 0.0061 | 14.5833 | 81.2500 | 0 | NA |
| `seed5_early` | 6 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0393 | 0.4912 | 0.1449 | 0.1531 | 2.3945 | 0.0000 | 0.2048 | 0.0206 | 7 | 0.0195 | 28.8000 | 71.2000 | 0 | NA |
| `seed5_early` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0352 | 0.4406 | 0.1073 | 0.1565 | 2.3345 | 0.0000 | 0.1997 | 0.0102 | 3 | 0.0142 | 25.6000 | 74.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_early` | 8 | 1 | 7 | 224.7500 | 48 | 250 | -0.1337 | -0.0107 | 0.1099 | 0.1401 | 0.2260 | 0.0148 | 4.6250 | 0.0092 | 23.9229 | 75.5062 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
