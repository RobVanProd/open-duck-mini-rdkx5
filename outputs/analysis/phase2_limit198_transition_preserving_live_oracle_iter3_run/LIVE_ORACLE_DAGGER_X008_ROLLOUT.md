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
terrain_hfield_z_scale: `0.0026`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |
| `student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3269 | 0.1320 | 0.1522 | 1.7502 | 0.0000 | 0.0000 | 0.1892 | 0.0123 | 18 | 0.0116 | 25.2000 | 74.8000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3269 | 0.0262 | 0.1320 | 0.1522 | 0.0000 | 0.0000 | 0.0123 | 18.0000 | 0.0116 | 25.2000 | 74.8000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
