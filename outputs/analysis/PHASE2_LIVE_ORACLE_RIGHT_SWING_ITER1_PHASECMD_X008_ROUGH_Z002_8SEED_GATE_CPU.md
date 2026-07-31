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
| `live_oracle_iter1_phasecmd` | 0 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0337 | 0.4216 | 0.1047 | 0.1519 | 2.4395 | 0.0000 | 0.1988 | 0.0115 | 4 | 0.0022 | 24.4000 | 75.6000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0331 | 0.4138 | 0.1132 | 0.1563 | 2.2543 | 0.0000 | 0.1960 | 0.0121 | 4 | 0.0171 | 25.6000 | 74.0000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0428 | 0.5352 | 0.1048 | 0.1511 | 2.3467 | 0.0000 | 0.1907 | 0.0113 | 7 | 0.0064 | 28.4000 | 71.6000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0283 | 0.3542 | 0.1150 | 0.1553 | 2.4236 | 0.0000 | 0.1905 | 0.0110 | 5 | 0.0034 | 25.6000 | 74.4000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 4 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0334 | 0.4178 | 0.1004 | 0.1506 | 2.4047 | 0.0000 | 0.1951 | 0.0107 | 4 | 0.0024 | 18.4000 | 81.6000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 53 | `fall_or_nan` | -0.2401 | -3.0018 | 0.0663 | 0.0910 | 3.0416 | 1.0416 | 0.1878 | 0.0327 | 2 | 0.0508 | 22.6415 | 69.8113 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0283 | 0.3542 | 0.0944 | 0.1532 | 2.3940 | 0.0000 | 0.1983 | 0.0199 | 4 | 0.0080 | 20.8000 | 79.2000 | 0 | NA |
| `live_oracle_iter1_phasecmd` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0358 | 0.4469 | 0.1071 | 0.1565 | 2.4527 | 0.0000 | 0.1975 | 0.0105 | 4 | 0.0100 | 24.0000 | 76.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_iter1_phasecmd` | 8 | 1 | 7 | 225.3750 | 53 | 250 | -0.0073 | -0.0006 | 0.1007 | 0.1457 | 0.1302 | 0.0150 | 4.2500 | 0.0125 | 23.7302 | 75.2764 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
