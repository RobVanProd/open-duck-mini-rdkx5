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
seeds: `[0, 2]`
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
| `lk098` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0358 | 0.4477 | 0.1447 | 0.1519 | 1.7851 | 0.0000 | 0.2016 | 0.0141 | 7 | 0.0060 | 22.8000 | 77.2000 | 4 | 0.7500 |
| `lk098` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0344 | 0.4300 | 0.1353 | 0.1511 | 1.7747 | 0.0000 | 0.2026 | 0.0150 | 8 | 0.0063 | 26.0000 | 74.0000 | 4 | 0.7500 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lk098` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.4388 | 0.0351 | 0.1400 | 0.1515 | 0.0000 | 0.0145 | 7.5000 | 0.0061 | 24.4000 | 75.6000 | 4.0000 | 0.7500 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
