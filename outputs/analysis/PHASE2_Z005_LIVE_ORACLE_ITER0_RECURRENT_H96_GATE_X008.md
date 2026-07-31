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
terrain_hfield_z_scale: `0.005`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter0_recurrent` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 173 | `fall_or_nan` | -0.1052 | -1.3147 | 0.1336 | 0.0559 | 5.2400 | 3.2400 | 3.2400 | 0.2141 | 0.0359 | 6 | 0.0112 | 26.5896 | 72.8324 | 0 | NA |
| `iter0_recurrent` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 87 | `fall_or_nan` | 0.1842 | 2.3019 | 1.1193 | 0.0137 | 5.2400 | 3.2400 | 3.2400 | 0.2304 | 0.0603 | 2 | 0.0099 | 34.4828 | 63.2184 | 0 | NA |
| `iter0_recurrent` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 274 | `fall_or_nan` | 0.0646 | 0.8071 | 0.4901 | 0.0154 | 5.2400 | 3.2400 | 3.2400 | 0.2043 | 0.0616 | 6 | 0.0098 | 18.6131 | 81.0219 | 0 | NA |
| `iter0_recurrent` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 77 | `fall_or_nan` | -0.2457 | -3.0716 | 0.1660 | 0.0684 | 5.2400 | 3.2400 | 3.2400 | 0.2125 | 0.0331 | 1 | 0.0078 | 14.2857 | 83.1169 | 0 | NA |
| `iter0_recurrent` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 133 | `fall_or_nan` | -0.1243 | -1.5537 | 0.0418 | 0.0600 | 5.2400 | 3.2400 | 3.2400 | 0.1895 | 0.0332 | 2 | 0.0068 | 15.7895 | 83.4586 | 0 | NA |
| `iter0_recurrent` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 68 | `fall_or_nan` | -0.2129 | -2.6608 | 0.0863 | 0.0726 | 5.2400 | 3.2400 | 3.2400 | 0.2503 | 0.0334 | 3 | 0.0083 | 25.0000 | 69.1176 | 0 | NA |
| `iter0_recurrent` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 95 | `fall_or_nan` | -0.1689 | -2.1106 | 0.1507 | 0.0695 | 5.2400 | 3.2400 | 3.2400 | 0.2408 | 0.0340 | 1 | 0.0099 | 23.1579 | 74.7368 | 0 | NA |
| `iter0_recurrent` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 85 | `fall_or_nan` | -0.1831 | -2.2882 | 0.1193 | 0.0900 | 5.2400 | 3.2400 | 3.2400 | 0.1992 | 0.0326 | 3 | 0.0075 | 24.7059 | 71.7647 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter0_recurrent` | 8 | 8 | 0 | 124.0000 | 68 | 274 | -1.2363 | -0.0989 | 0.2884 | 0.0557 | 3.2400 | 3.2400 | 0.0405 | 3.0000 | 0.0089 | 22.8281 | 74.9084 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
