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
| `contactphase` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 250 | `duration_complete` | 0.0338 | 0.4221 | 0.0996 | 0.1519 | 2.4169 | 0.0180 | 0.1966 | 0.0120 | 6 | 0.0040 | 23.2000 | 76.8000 | 0 | NA |
| `contactphase` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0336 | 0.4200 | 0.1172 | 0.1563 | 2.2565 | 0.0000 | 0.1918 | 0.0124 | 3 | 0.0144 | 28.4000 | 71.2000 | 0 | NA |
| `contactphase` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0381 | 0.4762 | 0.1001 | 0.1511 | 2.3493 | 0.0000 | 0.1934 | 0.0113 | 6 | 0.0063 | 29.6000 | 70.4000 | 0 | NA |
| `contactphase` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0192 | 0.2403 | 0.1129 | 0.1555 | 2.3859 | 0.0000 | 0.1946 | 0.0119 | 5 | 0.0063 | 18.4000 | 81.6000 | 0 | NA |
| `contactphase` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0364 | 0.4551 | 0.1051 | 0.1506 | 2.3527 | 0.0000 | 0.1943 | 0.0102 | 5 | 0.0061 | 23.6000 | 76.4000 | 0 | NA |
| `contactphase` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3092 | -3.8648 | 0.0611 | 0.0650 | 1.9697 | 0.0000 | 0.1970 | 0.0280 | 2 | 0.0054 | 6.2500 | 85.4167 | 0 | NA |
| `contactphase` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0391 | 0.4888 | 0.1225 | 0.1531 | 2.2739 | 0.0000 | 0.1927 | 0.0190 | 6 | 0.0175 | 28.0000 | 72.0000 | 0 | NA |
| `contactphase` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0382 | 0.4769 | 0.1049 | 0.1565 | 2.3176 | 0.0000 | 0.1942 | 0.0113 | 3 | 0.0138 | 27.6000 | 72.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `contactphase` | 8 | 1 | 7 | 224.7500 | 48 | 250 | -0.1107 | -0.0089 | 0.1029 | 0.1425 | 0.0022 | 0.0145 | 4.5000 | 0.0092 | 23.1313 | 75.7771 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
