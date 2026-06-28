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
| `seed5_capped` | 0 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0311 | 0.3891 | 0.1001 | 0.1519 | 2.4003 | 0.0000 | 0.1968 | 0.0121 | 5 | 0.0024 | 22.0000 | 78.0000 | 0 | NA |
| `seed5_capped` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0261 | 0.3263 | 0.1098 | 0.1563 | 2.4240 | 0.0000 | 0.1964 | 0.0113 | 4 | 0.0161 | 21.6000 | 78.0000 | 0 | NA |
| `seed5_capped` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0363 | 0.4540 | 0.1059 | 0.1511 | 2.3600 | 0.0000 | 0.1947 | 0.0118 | 6 | 0.0071 | 26.0000 | 74.0000 | 0 | NA |
| `seed5_capped` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0309 | 0.3865 | 0.1173 | 0.1555 | 2.3240 | 0.0000 | 0.1889 | 0.0105 | 5 | 0.0038 | 23.2000 | 76.8000 | 0 | NA |
| `seed5_capped` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0356 | 0.4445 | 0.0961 | 0.1506 | 2.4347 | 0.0000 | 0.1960 | 0.0108 | 4 | 0.0067 | 21.6000 | 78.4000 | 0 | NA |
| `seed5_capped` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 55 | `fall_or_nan` | -0.2492 | -3.1144 | 0.0691 | 0.0819 | 3.2094 | 0.2094 | 0.2049 | 0.0317 | 2 | 0.0069 | 7.2727 | 81.8182 | 0 | NA |
| `seed5_capped` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0357 | 0.4468 | 0.1014 | 0.1532 | 2.4606 | 0.0000 | 0.1993 | 0.0192 | 6 | 0.0093 | 26.0000 | 74.0000 | 0 | NA |
| `seed5_capped` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0288 | 0.3602 | 0.0964 | 0.1565 | 2.4514 | 0.0000 | 0.1984 | 0.0113 | 3 | 0.0044 | 22.4000 | 77.6000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_capped` | 8 | 1 | 7 | 225.6250 | 55 | 250 | -0.0384 | -0.0031 | 0.0995 | 0.1446 | 0.0262 | 0.0148 | 4.3750 | 0.0071 | 21.2591 | 77.3273 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
