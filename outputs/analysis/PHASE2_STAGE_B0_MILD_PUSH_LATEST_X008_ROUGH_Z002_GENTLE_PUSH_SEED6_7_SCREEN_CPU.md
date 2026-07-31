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
seeds: `[6, 7]`
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
| `b0` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0394 | 0.4930 | 0.1436 | 0.1530 | 1.7457 | 0.0000 | 0.1992 | 0.0145 | 6 | 0.0135 | 27.6000 | 72.4000 | 4 | 1.0000 |
| `b0` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0356 | 0.4455 | 0.1277 | 0.1564 | 1.7892 | 0.0000 | 0.1997 | 0.0108 | 5 | 0.0168 | 24.8000 | 75.2000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.4693 | 0.0375 | 0.1356 | 0.1547 | 0.0000 | 0.0126 | 5.5000 | 0.0151 | 26.2000 | 73.8000 | 3.5000 | 1.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
