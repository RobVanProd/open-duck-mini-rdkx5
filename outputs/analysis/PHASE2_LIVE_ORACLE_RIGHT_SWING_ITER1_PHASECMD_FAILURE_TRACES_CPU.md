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
seeds: `[0, 4, 5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[0, 4, 5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_iter1_phasecmd` | 0 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0337 | 0.4216 | 0.1047 | 0.1519 | 2.4395 | 0.0000 | 0.1988 | 0.0115 | 4 | 0.0022 | 24.4000 | 75.6000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 4 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0334 | 0.4178 | 0.1004 | 0.1506 | 2.4047 | 0.0000 | 0.1951 | 0.0107 | 4 | 0.0024 | 18.4000 | 81.6000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 53 | `fall_or_nan` | -0.2401 | -3.0018 | 0.0663 | 0.0910 | 3.0416 | 1.0416 | 0.1878 | 0.0327 | 2 | 0.0508 | 22.6415 | 69.8113 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_iter1_phasecmd` | 3 | 1 | 2 | 184.3333 | 53 | 250 | -0.7208 | -0.0577 | 0.0905 | 0.1312 | 0.3472 | 0.0183 | 3.3333 | 0.0185 | 21.8138 | 75.6704 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
