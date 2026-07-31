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
| `smooth` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0344 | 0.4294 | 0.1024 | 0.1519 | 2.4061 | 0.0000 | 0.1946 | 0.0114 | 6 | 0.0079 | 23.6000 | 76.4000 | 0 | NA |
| `smooth` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0338 | 0.4231 | 0.1201 | 0.1563 | 2.3783 | 0.0000 | 0.1936 | 0.0122 | 4 | 0.0193 | 26.8000 | 72.8000 | 0 | NA |
| `smooth` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0408 | 0.5105 | 0.1052 | 0.1511 | 2.3437 | 0.0000 | 0.1931 | 0.0117 | 5 | 0.0094 | 30.0000 | 70.0000 | 0 | NA |
| `smooth` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0263 | 0.3287 | 0.1127 | 0.1548 | 2.3954 | 0.0000 | 0.1888 | 0.0114 | 6 | 0.0044 | 21.2000 | 78.8000 | 0 | NA |
| `smooth` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0351 | 0.4382 | 0.1048 | 0.1507 | 2.3589 | 0.0000 | 0.1970 | 0.0105 | 3 | 0.0060 | 20.8000 | 79.2000 | 0 | NA |
| `smooth` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0339 | 0.4235 | 0.1117 | 0.1464 | 2.3122 | 0.0000 | 0.1968 | 0.0183 | 5 | 0.0076 | 16.4000 | 82.8000 | 0 | NA |
| `smooth` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0360 | 0.4502 | 0.1067 | 0.1531 | 2.3998 | 0.0000 | 0.1944 | 0.0171 | 7 | 0.0074 | 27.6000 | 72.4000 | 0 | NA |
| `smooth` | 7 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0284 | 0.3545 | 0.1016 | 0.1565 | 2.4120 | 0.0000 | 0.2005 | 0.0109 | 3 | 0.0121 | 21.6000 | 78.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `smooth` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4197 | 0.0336 | 0.1081 | 0.1526 | 0.0000 | 0.0129 | 4.8750 | 0.0092 | 23.5000 | 76.3500 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
