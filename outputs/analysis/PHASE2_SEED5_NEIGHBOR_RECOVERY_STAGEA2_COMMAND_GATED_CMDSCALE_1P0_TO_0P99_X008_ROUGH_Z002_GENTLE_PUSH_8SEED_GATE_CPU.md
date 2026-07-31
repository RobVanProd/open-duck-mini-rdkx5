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
| `scaled` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0328 | 0.4096 | 0.0993 | 0.1519 | 2.3681 | 0.0000 | 0.1919 | 0.0119 | 5 | 0.0047 | 23.2000 | 76.8000 | 4 | 0.7500 |
| `scaled` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0317 | 0.3957 | 0.1258 | 0.1563 | 2.3079 | 0.0000 | 0.1934 | 0.0122 | 4 | 0.0185 | 26.4000 | 73.2000 | 4 | 1.0000 |
| `scaled` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0380 | 0.4744 | 0.1126 | 0.1511 | 2.3183 | 0.0000 | 0.1934 | 0.0120 | 5 | 0.0078 | 28.8000 | 71.2000 | 4 | 0.7500 |
| `scaled` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0247 | 0.3085 | 0.1324 | 0.1548 | 2.3418 | 0.0000 | 0.1861 | 0.0117 | 5 | 0.0048 | 21.6000 | 78.4000 | 4 | 1.0000 |
| `scaled` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0358 | 0.4478 | 0.1053 | 0.1507 | 2.3445 | 0.0000 | 0.1912 | 0.0109 | 6 | 0.0098 | 25.2000 | 74.8000 | 4 | 0.7500 |
| `scaled` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0340 | 0.4250 | 0.1061 | 0.1464 | 2.3292 | 0.0000 | 0.1985 | 0.0183 | 5 | 0.0075 | 17.2000 | 82.0000 | 4 | 1.0000 |
| `scaled` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0311 | 0.3888 | 0.1132 | 0.1531 | 2.3665 | 0.0000 | 0.1934 | 0.0172 | 5 | 0.0081 | 24.0000 | 76.0000 | 4 | 1.0000 |
| `scaled` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0298 | 0.3731 | 0.0976 | 0.1565 | 2.3383 | 0.0000 | 0.1974 | 0.0118 | 4 | 0.0131 | 24.0000 | 76.0000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `scaled` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4029 | 0.0322 | 0.1116 | 0.1526 | 0.0000 | 0.0132 | 4.8750 | 0.0093 | 23.8000 | 76.0500 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
