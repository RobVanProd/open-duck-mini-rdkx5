# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
min_swing_segments_per_foot: `0`
min_swing_rel_x_range_p95_m: `0.0`
min_swing_peak_lift_m: `0.0`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0166 | 0.1527 | 0.3546 | 0.0000 | 0.0631 | 0.0015 | 0 | 0.0000 | 0.4000 | 99.6000 | 0 | NA |
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0414 | 0.1565 | 0.2922 | 0.0000 | 0.0637 | 0.0062 | 1 | 0.0004 | 1.0667 | 98.8000 | 0 | NA |
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | NA | 0.0308 | 0.1514 | 0.3774 | 0.0000 | 0.0658 | 0.0081 | 1 | 0.0054 | 0.8000 | 99.2000 | 0 | NA |
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0021 | NA | 0.0129 | 0.1559 | 0.3862 | 0.0000 | 0.0624 | 0.0056 | 0 | 0.0000 | 0.1333 | 99.8667 | 0 | NA |
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0014 | NA | 0.0092 | 0.1508 | 0.3645 | 0.0000 | 0.0612 | 0.0017 | 0 | 0.0000 | 0.2667 | 99.7333 | 0 | NA |
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 61 | `fall_or_nan` | -0.2589 | NA | 0.0759 | 0.0512 | 1.2575 | 0.0000 | 0.1953 | 0.0308 | 2 | 0.0080 | 8.1967 | 85.2459 | 0 | NA |
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0003 | NA | 0.0001 | 0.1531 | 0.2786 | 0.0000 | 0.0553 | 0.0194 | 1 | 0.0080 | 1.4667 | 98.5333 | 0 | NA |
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0003 | NA | 0.0245 | 0.1565 | 0.3920 | 0.0000 | 0.0642 | 0.0141 | 0 | 0.0000 | 0.9333 | 99.0667 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase2_stagea2_seed5_recovery_command_gated_gain099_20260629` | 8 | 1 | 7 | 663.8750 | 61 | 750 | NA | -0.0322 | 0.0264 | 0.1410 | 0.0000 | 0.0109 | 0.6250 | 0.0027 | 1.6579 | 97.5057 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
