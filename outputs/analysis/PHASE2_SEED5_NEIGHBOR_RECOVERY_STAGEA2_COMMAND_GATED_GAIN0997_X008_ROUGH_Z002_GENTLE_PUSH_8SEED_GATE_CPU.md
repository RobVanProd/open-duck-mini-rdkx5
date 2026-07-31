# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `0.997`
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
| `gated` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0334 | 0.4180 | 0.1045 | 0.1519 | 2.4053 | 0.0000 | 0.1968 | 0.0123 | 5 | 0.0072 | 22.4000 | 77.6000 | 4 | 0.7500 |
| `gated` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0316 | 0.3946 | 0.1269 | 0.1563 | 2.3295 | 0.0000 | 0.1965 | 0.0121 | 6 | 0.0178 | 26.4000 | 73.2000 | 4 | 1.0000 |
| `gated` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0402 | 0.5022 | 0.1120 | 0.1511 | 2.3419 | 0.0000 | 0.1946 | 0.0117 | 7 | 0.0089 | 31.6000 | 68.4000 | 4 | 0.7500 |
| `gated` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0254 | 0.3175 | 0.1294 | 0.1548 | 2.4012 | 0.0000 | 0.1873 | 0.0111 | 5 | 0.0043 | 23.2000 | 76.8000 | 4 | 1.0000 |
| `gated` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0369 | 0.4610 | 0.1093 | 0.1507 | 2.4046 | 0.0000 | 0.1969 | 0.0108 | 4 | 0.0102 | 24.4000 | 75.6000 | 4 | 0.7500 |
| `gated` | 5 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 250 | `duration_complete` | 0.0350 | 0.4379 | 0.1046 | 0.1464 | 2.3803 | 0.0806 | 0.1978 | 0.0182 | 6 | 0.0073 | 18.0000 | 81.2000 | 4 | 1.0000 |
| `gated` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0362 | 0.4519 | 0.1164 | 0.1531 | 2.4060 | 0.0000 | 0.1971 | 0.0170 | 7 | 0.0072 | 28.0000 | 72.0000 | 4 | 1.0000 |
| `gated` | 7 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0294 | 0.3678 | 0.1010 | 0.1565 | 2.4006 | 0.0000 | 0.2010 | 0.0102 | 4 | 0.0045 | 22.8000 | 77.2000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4189 | 0.0335 | 0.1130 | 0.1526 | 0.0101 | 0.0129 | 5.5000 | 0.0084 | 24.6000 | 75.2500 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
