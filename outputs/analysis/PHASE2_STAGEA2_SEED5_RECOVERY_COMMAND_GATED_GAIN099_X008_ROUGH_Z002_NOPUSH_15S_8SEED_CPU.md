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
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0315 | 0.3934 | 0.1081 | 0.1519 | 2.3978 | 0.0000 | 0.1931 | 0.0116 | 14 | 0.0135 | 23.2000 | 76.8000 | 0 | NA |
| `gain099` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0349 | 0.4363 | 0.1130 | 0.1563 | 2.3544 | 0.0000 | 0.1903 | 0.0123 | 19 | 0.0179 | 28.0000 | 71.8667 | 0 | NA |
| `gain099` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0340 | 0.4249 | 0.1080 | 0.1511 | 2.3584 | 0.0000 | 0.1925 | 0.0114 | 10 | 0.0112 | 24.5333 | 75.4667 | 0 | NA |
| `gain099` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0294 | 0.3677 | 0.1103 | 0.1548 | 2.3710 | 0.0000 | 0.1916 | 0.0115 | 11 | 0.0159 | 23.2000 | 76.8000 | 0 | NA |
| `gain099` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0344 | 0.4301 | 0.1035 | 0.1507 | 2.3919 | 0.0000 | 0.1916 | 0.0116 | 17 | 0.0049 | 24.8000 | 75.2000 | 0 | NA |
| `gain099` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0310 | 0.3873 | 0.1140 | 0.1464 | 2.3568 | 0.0000 | 0.1975 | 0.0187 | 14 | 0.0073 | 21.7333 | 78.0000 | 0 | NA |
| `gain099` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0342 | 0.4280 | 0.1036 | 0.1531 | 2.3573 | 0.0000 | 0.1915 | 0.0173 | 21 | 0.0069 | 26.9333 | 73.0667 | 0 | NA |
| `gain099` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0300 | 0.3748 | 0.1056 | 0.1565 | 2.3747 | 0.0000 | 0.1920 | 0.0117 | 14 | 0.0136 | 24.4000 | 75.6000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4053 | 0.0324 | 0.1083 | 0.1526 | 0.0000 | 0.0133 | 15.0000 | 0.0114 | 24.6000 | 75.3500 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
