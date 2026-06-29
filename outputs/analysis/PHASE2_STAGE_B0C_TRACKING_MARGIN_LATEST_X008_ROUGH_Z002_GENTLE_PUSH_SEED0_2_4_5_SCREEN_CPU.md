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
seeds: `[0, 2, 4, 5]`
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
| `b0c_245` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0389 | 0.4867 | 0.1410 | 0.1519 | 1.7774 | 0.0000 | 0.2081 | 0.0149 | 6 | 0.0134 | 26.8000 | 73.2000 | 4 | 0.7500 |
| `b0c_245` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0324 | 0.4052 | 0.1296 | 0.1511 | 1.7780 | 0.0000 | 0.2024 | 0.0127 | 7 | 0.0091 | 23.6000 | 76.4000 | 4 | 0.7500 |
| `b0c_245` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0380 | 0.4755 | 0.1298 | 0.1506 | 1.7929 | 0.0000 | 0.1997 | 0.0113 | 5 | 0.0082 | 20.0000 | 80.0000 | 4 | 0.7500 |
| `b0c_245` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0405 | 0.5057 | 0.1296 | 0.1462 | 1.7827 | 0.0000 | 0.1993 | 0.0184 | 6 | 0.0086 | 22.0000 | 77.2000 | 4 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0c_245` | 4 | 0 | 4 | 250.0000 | 250 | 250 | 0.4683 | 0.0375 | 0.1325 | 0.1500 | 0.0000 | 0.0143 | 6.0000 | 0.0098 | 23.1000 | 76.7000 | 4.0000 | 0.8125 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
