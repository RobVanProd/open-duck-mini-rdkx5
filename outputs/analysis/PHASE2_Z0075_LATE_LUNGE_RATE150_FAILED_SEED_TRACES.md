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
seeds: `[0, 1, 2, 3, 4, 5, 6]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter9_late_lunge_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 150 | `fall_or_nan` | 0.1427 | 1.7842 | 0.8630 | 0.0025 | 1.6139 | 0.0000 | 0.1199 | 0.2049 | 0.0573 | 3 | 0.0071 | 17.3333 | 81.3333 | 2 | 0.5000 |
| `iter9_late_lunge_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 580 | `fall_or_nan` | 0.0583 | 0.7284 | 0.2497 | 0.0124 | 1.5416 | 0.0000 | 1.0405 | 0.1847 | 0.0632 | 12 | 0.0122 | 26.2069 | 73.4483 | 10 | 0.9000 |
| `iter9_late_lunge_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 154 | `fall_or_nan` | 0.1308 | 1.6349 | 0.8069 | 0.0185 | 1.5934 | 0.0000 | 0.0000 | 0.1941 | 0.0603 | 2 | 0.0055 | 18.8312 | 80.5195 | 2 | 0.5000 |
| `iter9_late_lunge_rate150` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0269 | 0.3365 | 0.1525 | 0.1558 | 1.5781 | 0.0000 | 0.2400 | 0.1859 | 0.0150 | 17 | 0.0162 | 22.5333 | 77.4667 | 13 | 0.9231 |
| `iter9_late_lunge_rate150` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 277 | `fall_or_nan` | 0.0923 | 1.1543 | 0.5693 | -0.0053 | 1.5978 | 0.0000 | 0.0537 | 0.1822 | 0.0599 | 6 | 0.0086 | 19.1336 | 80.1444 | 4 | 0.7500 |
| `iter9_late_lunge_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 46 | `fall_or_nan` | -0.3199 | -3.9985 | 0.0578 | 0.0695 | 1.6712 | 0.0000 | 0.0000 | 0.2101 | 0.0289 | 1 | 0.0080 | 17.3913 | 76.0870 | 0 | NA |
| `iter9_late_lunge_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 425 | `fall_or_nan` | 0.0707 | 0.8839 | 0.3439 | -0.0021 | 1.5446 | 0.0000 | 1.5385 | 0.1847 | 0.0630 | 10 | 0.0185 | 24.4706 | 75.0588 | 7 | 0.8571 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter9_late_lunge_rate150` | 7 | 6 | 1 | 340.2857 | 46 | 750 | 0.3605 | 0.0288 | 0.4347 | 0.0359 | 0.0000 | 0.4275 | 0.0497 | 7.2857 | 0.0109 | 20.8429 | 77.7226 | 5.4286 | 0.7384 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
