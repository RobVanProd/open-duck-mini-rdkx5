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
| `iter0_phase_mod` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0280 | 0.3499 | 0.1384 | 0.1527 | 1.9881 | 0.0000 | 0.0777 | 0.1963 | 0.0141 | 13 | 0.0071 | 21.7333 | 78.2667 | 0 | NA |
| `iter0_phase_mod` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0276 | 0.3454 | 0.1340 | 0.1565 | 1.9881 | 0.0000 | 0.0598 | 0.1928 | 0.0121 | 13 | 0.0094 | 21.4667 | 78.4000 | 0 | NA |
| `iter0_phase_mod` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0301 | 0.3768 | 0.1230 | 0.1514 | 1.9850 | 0.0000 | 0.0791 | 0.1961 | 0.0112 | 12 | 0.0097 | 23.0667 | 76.9333 | 0 | NA |
| `iter0_phase_mod` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0204 | 0.2550 | 0.1464 | 0.1559 | 1.9817 | 0.0000 | 0.0429 | 0.1886 | 0.0148 | 16 | 0.0087 | 19.0667 | 80.9333 | 0 | NA |
| `iter0_phase_mod` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0287 | 0.3587 | 0.1147 | 0.1508 | 1.9993 | 0.0000 | 0.0273 | 0.1930 | 0.0116 | 12 | 0.0045 | 20.1333 | 79.8667 | 0 | NA |
| `iter0_phase_mod` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 54 | `fall_or_nan` | -0.2817 | -3.5207 | 0.0602 | 0.0605 | 1.6283 | 0.0000 | 0.0000 | 0.1984 | 0.0307 | 1 | 0.0087 | 14.8148 | 79.6296 | 0 | NA |
| `iter0_phase_mod` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0300 | 0.3752 | 0.1257 | 0.1532 | 1.9930 | 0.0000 | 0.0223 | 0.1921 | 0.0196 | 19 | 0.0100 | 24.4000 | 75.6000 | 0 | NA |
| `iter0_phase_mod` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0273 | 0.3412 | 0.1281 | 0.1564 | 1.9942 | 0.0000 | 0.0000 | 0.1961 | 0.0130 | 6 | 0.0166 | 21.0667 | 78.9333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter0_phase_mod` | 8 | 1 | 7 | 663.0000 | 54 | 750 | -0.1398 | -0.0112 | 0.1213 | 0.1422 | 0.0000 | 0.0387 | 0.0159 | 11.5000 | 0.0093 | 20.7185 | 78.5704 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
