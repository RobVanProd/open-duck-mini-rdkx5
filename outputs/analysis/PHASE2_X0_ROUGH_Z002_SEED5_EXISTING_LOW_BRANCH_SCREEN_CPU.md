# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase1` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0107 | NA | 0.0287 | 0.1462 | 0.8050 | 0.0000 | 0.1111 | 0.0199 | 1 | 0.0036 | 0.8000 | 98.4000 | 0 | NA |
| `stage_a2` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0110 | NA | 0.0385 | 0.1462 | 0.9804 | 0.0000 | 0.1056 | 0.0198 | 1 | 0.0037 | 1.2000 | 98.0000 | 0 | NA |
| `old_x0safe` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 82 | `fall_or_nan` | -0.1801 | NA | 0.1184 | 0.0643 | 1.4307 | 0.0000 | 0.1574 | 0.0322 | 1 | 0.0036 | 4.8780 | 90.2439 | 0 | NA |
| `scale075` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 58 | `fall_or_nan` | -0.2672 | NA | 0.0672 | 0.0545 | 1.4291 | 0.0000 | 0.1967 | 0.0317 | 2 | 0.0073 | 10.3448 | 81.0345 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase1` | 1 | 0 | 1 | 250.0000 | 250 | 250 | NA | 0.0107 | 0.0287 | 0.1462 | 0.0000 | 0.0199 | 1.0000 | 0.0036 | 0.8000 | 98.4000 | 0.0000 | NA |
| `stage_a2` | 1 | 0 | 1 | 250.0000 | 250 | 250 | NA | 0.0110 | 0.0385 | 0.1462 | 0.0000 | 0.0198 | 1.0000 | 0.0037 | 1.2000 | 98.0000 | 0.0000 | NA |
| `old_x0safe` | 1 | 1 | 0 | 82.0000 | 82 | 82 | NA | -0.1801 | 0.1184 | 0.0643 | 0.0000 | 0.0322 | 1.0000 | 0.0036 | 4.8780 | 90.2439 | 0.0000 | NA |
| `scale075` | 1 | 1 | 0 | 58.0000 | 58 | 58 | NA | -0.2672 | 0.0672 | 0.0545 | 0.0000 | 0.0317 | 2.0000 | 0.0073 | 10.3448 | 81.0345 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
