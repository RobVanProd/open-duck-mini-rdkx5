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
seeds: `[2, 4]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.001`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `2026_06_28_093051_35120` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0277 | 0.3457 | 0.1125 | 0.1510 | 1.5148 | 0.0000 | 0.1880 | 0.0102 | 1 | 0.0063 | 17.2000 | 82.8000 | 0 | NA |
| `2026_06_28_093051_35120` | 4 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0203 | 0.2539 | 0.1004 | 0.1506 | 1.4600 | 0.0000 | 0.1708 | 0.0081 | 0 | 0.0000 | 7.2000 | 92.8000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `2026_06_28_093051_35120` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.2998 | 0.0240 | 0.1065 | 0.1508 | 0.0000 | 0.0092 | 0.5000 | 0.0032 | 12.2000 | 87.8000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
