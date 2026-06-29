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
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0295 | 0.3689 | 0.1375 | 0.1527 | 2.3867 | 0.0000 | 0.1954 | 0.0130 | 22 | 0.0097 | 23.3333 | 76.6667 | 0 | NA |
| `gain099` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0345 | 0.4313 | 0.1229 | 0.1565 | 2.3839 | 0.0000 | 0.1921 | 0.0123 | 20 | 0.0101 | 28.1333 | 71.7333 | 0 | NA |
| `gain099` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0345 | 0.4309 | 0.1279 | 0.1514 | 2.3611 | 0.0000 | 0.1937 | 0.0133 | 15 | 0.0222 | 26.9333 | 73.0667 | 0 | NA |
| `gain099` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3304 | 0.1363 | 0.1559 | 2.3679 | 0.0000 | 0.1929 | 0.0126 | 17 | 0.0194 | 23.3333 | 76.6667 | 0 | NA |
| `gain099` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0346 | 0.4327 | 0.1356 | 0.1508 | 2.3941 | 0.0000 | 0.1922 | 0.0130 | 18 | 0.0087 | 24.9333 | 75.0667 | 0 | NA |
| `gain099` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | `fall_or_nan` | -0.2654 | -3.3180 | 0.0683 | 0.0677 | 1.9250 | 0.0000 | 0.1968 | 0.0286 | 0 | 0.0000 | 7.1429 | 91.0714 | 0 | NA |
| `gain099` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0333 | 0.4159 | 0.1156 | 0.1533 | 2.4032 | 0.0000 | 0.1926 | 0.0190 | 23 | 0.0043 | 26.4000 | 73.6000 | 0 | NA |
| `gain099` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0287 | 0.3584 | 0.1171 | 0.1564 | 2.3814 | 0.0000 | 0.1941 | 0.0137 | 18 | 0.0146 | 23.0667 | 76.9333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 8 | 1 | 7 | 663.2500 | 56 | 750 | -0.0687 | -0.0055 | 0.1201 | 0.1431 | 0.0000 | 0.0157 | 16.6250 | 0.0111 | 22.9095 | 76.8506 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
