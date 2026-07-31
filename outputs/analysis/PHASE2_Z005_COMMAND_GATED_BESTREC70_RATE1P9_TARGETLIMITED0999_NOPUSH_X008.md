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
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0272 | 0.3394 | 0.1418 | 0.1527 | 1.9035 | 0.0000 | 0.0000 | 0.1962 | 0.0135 | 17 | 0.0102 | 20.2667 | 79.7333 | 0 | NA |
| `limited` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 711 | `fall_or_nan` | 0.0565 | 0.7064 | 0.2479 | 0.0045 | 1.9242 | 0.0000 | 0.0000 | 0.1880 | 0.0592 | 14 | 0.0186 | 25.3165 | 74.4023 | 0 | NA |
| `limited` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0300 | 0.3756 | 0.1211 | 0.1514 | 1.9185 | 0.0000 | 0.0000 | 0.1952 | 0.0121 | 14 | 0.0140 | 23.8667 | 76.1333 | 0 | NA |
| `limited` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0238 | 0.2979 | 0.1313 | 0.1559 | 1.9189 | 0.0000 | 0.0000 | 0.1903 | 0.0129 | 19 | 0.0127 | 19.8667 | 80.1333 | 0 | NA |
| `limited` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0331 | 0.4137 | 0.1247 | 0.1508 | 1.9198 | 0.0000 | 0.0000 | 0.1892 | 0.0133 | 14 | 0.0173 | 22.0000 | 78.0000 | 0 | NA |
| `limited` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.2711 | -3.3886 | 0.0707 | 0.0594 | 1.9015 | 0.0000 | 0.0000 | 0.1897 | 0.0321 | 1 | 0.0105 | 8.7719 | 82.4561 | 0 | NA |
| `limited` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0308 | 0.3849 | 0.1187 | 0.1532 | 1.9076 | 0.0000 | 0.0000 | 0.1956 | 0.0192 | 20 | 0.0092 | 23.6000 | 76.4000 | 0 | NA |
| `limited` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0291 | 0.3634 | 0.1258 | 0.1564 | 1.9214 | 0.0000 | 0.0000 | 0.1946 | 0.0130 | 11 | 0.0129 | 22.8000 | 77.2000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 8 | 2 | 6 | 658.5000 | 57 | 750 | -0.0634 | -0.0051 | 0.1352 | 0.1231 | 0.0000 | 0.0000 | 0.0219 | 13.7500 | 0.0132 | 20.8110 | 78.0573 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
