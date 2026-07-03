# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `2.0`
seeds: `[5]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0025`
reset_settle_ticks: `0`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `best_x0_s05_rate1p9_x008` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | -0.2724 | NA | 0.0735 | 0.0486 | 2.1520 | 0.0000 | 1.2818 | 0.1677 | 0.0289 | 2 | 0.0049 | 25.0000 | 71.6667 | 0 | NA |
| `best_x0_s06_rate1p9_x008` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.2871 | NA | 0.0598 | 0.0633 | 4.2458 | 1.7458 | 2.7400 | 0.2123 | 0.0324 | 4 | 0.0062 | 45.6140 | 43.8596 | 0 | NA |
| `best_x0_s07_rate1p9_x008` | 5 | `HOLD_CANDIDATE_TRACKING` | 100 | `duration_complete` | 0.0109 | NA | 0.0161 | 0.1457 | 3.3804 | 0.6304 | 2.7400 | 0.2067 | 0.0191 | 3 | 0.0108 | 16.0000 | 82.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `best_x0_s05_rate1p9_x008` | 1 | 1 | 0 | 60.0000 | 60 | 60 | NA | -0.2724 | 0.0735 | 0.0486 | 0.0000 | 1.2818 | 0.0289 | 2.0000 | 0.0049 | 25.0000 | 71.6667 | 0.0000 | NA |
| `best_x0_s06_rate1p9_x008` | 1 | 1 | 0 | 57.0000 | 57 | 57 | NA | -0.2871 | 0.0598 | 0.0633 | 1.7458 | 2.7400 | 0.0324 | 4.0000 | 0.0062 | 45.6140 | 43.8596 | 0.0000 | NA |
| `best_x0_s07_rate1p9_x008` | 1 | 0 | 1 | 100.0000 | 100 | 100 | NA | 0.0109 | 0.0161 | 0.1457 | 0.6304 | 2.7400 | 0.0191 | 3.0000 | 0.0108 | 16.0000 | 82.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
