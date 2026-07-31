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
push_recovery_window_s: `1.2`
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
| `iter26` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 554 | `fall_or_nan` | 0.0625 | 0.7815 | 0.3381 | 0.0121 | 1.5573 | 0.0000 | 0.0000 | 0.1806 | 0.0619 | 14 | 0.0144 | 24.9097 | 74.7292 | 9 | 0.7778 |
| `iter26` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 593 | `fall_or_nan` | -0.0001 | -0.0009 | 0.2058 | 0.0655 | 1.5513 | 0.0000 | 0.0000 | 0.1813 | 0.0350 | 11 | 0.0186 | 27.9933 | 71.5008 | 10 | 0.9000 |
| `iter26` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 286 | `fall_or_nan` | -0.0408 | -0.5101 | 0.1768 | 0.0726 | 1.5622 | 0.0000 | 0.0000 | 0.1813 | 0.0309 | 7 | 0.0222 | 20.9790 | 78.3217 | 5 | 0.6000 |
| `iter26` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0279 | 0.3491 | 0.1906 | 0.1582 | 1.5642 | 0.0000 | 0.0000 | 0.1887 | 0.0150 | 18 | 0.0229 | 25.4667 | 74.5333 | 13 | 0.9231 |
| `iter26` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 397 | `fall_or_nan` | 0.0742 | 0.9271 | 0.4199 | -0.0040 | 1.5609 | 0.0000 | 0.0000 | 0.1872 | 0.0599 | 7 | 0.0163 | 26.1965 | 73.5516 | 5 | 0.8000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter26` | 5 | 4 | 1 | 516.0000 | 286 | 750 | 0.3093 | 0.0247 | 0.2662 | 0.0609 | 0.0000 | 0.0000 | 0.0405 | 11.4000 | 0.0189 | 25.1090 | 74.5273 | 8.4000 | 0.8002 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
