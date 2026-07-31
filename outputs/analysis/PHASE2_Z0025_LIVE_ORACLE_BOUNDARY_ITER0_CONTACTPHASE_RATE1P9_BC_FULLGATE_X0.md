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
terrain_hfield_z_scale: `0.0025`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rate1p9` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0001 | NA | 0.0026 | 0.1520 | 0.0970 | 0.0000 | 0.0000 | 0.0374 | 0.0208 | 0 | 0.0000 | 0.2667 | 99.7333 | 0 | NA |
| `rate1p9` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0009 | NA | 0.0267 | 0.1564 | 0.0938 | 0.0000 | 0.0000 | 0.0399 | 0.0037 | 0 | 0.0000 | 0.8000 | 99.0667 | 0 | NA |
| `rate1p9` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0000 | NA | 0.0295 | 0.1513 | 0.0960 | 0.0000 | 0.0000 | 0.0385 | 0.0079 | 1 | 0.0039 | 0.6667 | 99.3333 | 0 | NA |
| `rate1p9` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0030 | NA | 0.0129 | 0.1545 | 0.0974 | 0.0000 | 0.0000 | 0.0363 | 0.0072 | 0 | 0.0000 | 0.1333 | 99.8667 | 0 | NA |
| `rate1p9` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0010 | NA | 0.0078 | 0.1508 | 0.0975 | 0.0000 | 0.0000 | 0.0379 | 0.0027 | 0 | 0.0000 | 0.2667 | 99.7333 | 0 | NA |
| `rate1p9` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 43 | `fall_or_nan` | -0.3468 | NA | 0.0553 | 0.0575 | 0.5823 | 0.0000 | 0.0000 | 0.2106 | 0.0304 | 1 | 0.0029 | 9.3023 | 86.0465 | 0 | NA |
| `rate1p9` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0000 | NA | 0.0070 | 0.1531 | 0.0973 | 0.0000 | 0.0000 | 0.0367 | 0.0245 | 1 | 0.0122 | 1.8667 | 98.1333 | 0 | NA |
| `rate1p9` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0005 | NA | 0.0307 | 0.1565 | 0.0937 | 0.0000 | 0.0000 | 0.0387 | 0.0181 | 0 | 0.0000 | 1.0667 | 98.9333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rate1p9` | 8 | 1 | 7 | 661.6250 | 43 | 750 | NA | -0.0438 | 0.0216 | 0.1415 | 0.0000 | 0.0000 | 0.0144 | 0.3750 | 0.0024 | 1.7961 | 97.6058 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
