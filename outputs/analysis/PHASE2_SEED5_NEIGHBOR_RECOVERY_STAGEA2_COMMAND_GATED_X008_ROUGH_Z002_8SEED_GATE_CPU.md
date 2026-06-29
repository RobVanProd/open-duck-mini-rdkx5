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
| `gated` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0305 | 0.3810 | 0.1113 | 0.1519 | 2.4109 | 0.0000 | 0.1977 | 0.0117 | 4 | 0.0049 | 22.4000 | 77.6000 | 0 | NA |
| `gated` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0333 | 0.4166 | 0.1236 | 0.1563 | 2.3657 | 0.0000 | 0.1980 | 0.0126 | 3 | 0.0198 | 26.8000 | 72.8000 | 0 | NA |
| `gated` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0415 | 0.5192 | 0.0966 | 0.1511 | 2.3297 | 0.0000 | 0.1955 | 0.0115 | 6 | 0.0064 | 28.8000 | 71.2000 | 0 | NA |
| `gated` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0253 | 0.3161 | 0.1103 | 0.1548 | 2.3597 | 0.0000 | 0.1887 | 0.0112 | 6 | 0.0032 | 21.2000 | 78.8000 | 0 | NA |
| `gated` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0358 | 0.4475 | 0.1051 | 0.1507 | 2.3387 | 0.0000 | 0.1984 | 0.0110 | 3 | 0.0063 | 22.4000 | 77.6000 | 0 | NA |
| `gated` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0340 | 0.4251 | 0.1088 | 0.1464 | 2.3694 | 0.0000 | 0.1950 | 0.0184 | 5 | 0.0071 | 16.8000 | 82.4000 | 0 | NA |
| `gated` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0375 | 0.4686 | 0.1021 | 0.1531 | 2.3931 | 0.0000 | 0.1932 | 0.0169 | 6 | 0.0084 | 28.0000 | 72.0000 | 0 | NA |
| `gated` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0277 | 0.3461 | 0.0995 | 0.1565 | 2.3553 | 0.0000 | 0.1974 | 0.0108 | 2 | 0.0048 | 22.4000 | 77.6000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4150 | 0.0332 | 0.1071 | 0.1526 | 0.0000 | 0.0130 | 4.3750 | 0.0076 | 23.6000 | 76.2500 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
