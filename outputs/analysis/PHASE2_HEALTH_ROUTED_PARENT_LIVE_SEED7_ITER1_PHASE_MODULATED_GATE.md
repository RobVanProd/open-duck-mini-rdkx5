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
seeds: `[0, 1, 2, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_seed7_phase_mod` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0242 | 0.3019 | 0.1692 | 0.1593 | 1.5729 | 0.0000 | 0.0000 | 0.1792 | 0.0158 | 14 | 0.0251 | 23.2000 | 76.8000 | 12 | 0.9167 |
| `live_seed7_phase_mod` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 150 | `fall_or_nan` | 0.1368 | 1.7102 | 0.8554 | 0.0127 | 1.5667 | 0.0000 | 0.0000 | 0.1958 | 0.0503 | 1 | 0.0015 | 16.0000 | 84.0000 | 2 | 1.0000 |
| `live_seed7_phase_mod` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0232 | 0.2900 | 0.1647 | 0.1593 | 1.5915 | 0.0000 | 0.0000 | 0.1813 | 0.0161 | 16 | 0.0194 | 22.2667 | 77.7333 | 13 | 0.9231 |
| `live_seed7_phase_mod` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0235 | 0.2937 | 0.1709 | 0.1590 | 1.5918 | 0.0000 | 0.0000 | 0.1832 | 0.0139 | 15 | 0.0159 | 23.3333 | 76.6667 | 13 | 0.9231 |
| `live_seed7_phase_mod` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 502 | `fall_or_nan` | 0.0618 | 0.7724 | 0.3591 | -0.0042 | 1.5836 | 0.0000 | 0.0000 | 0.1831 | 0.0620 | 10 | 0.0149 | 23.7052 | 75.8964 | 6 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_seed7_phase_mod` | 5 | 2 | 3 | 580.4000 | 150 | 750 | 0.6736 | 0.0539 | 0.3438 | 0.0972 | 0.0000 | 0.0000 | 0.0316 | 11.2000 | 0.0154 | 21.7010 | 78.2193 | 9.2000 | 0.9526 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
