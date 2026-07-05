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
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 115 | `fall_or_nan` | 0.1803 | 2.2538 | 0.9956 | -0.0053 | 1.6360 | 0.0000 | 0.0000 | 0.1987 | 0.0552 | 0 | 0.0000 | 12.1739 | 86.9565 | 1 | 0.0000 |
| `student` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 229 | `fall_or_nan` | 0.0984 | 1.2296 | 0.6725 | 0.0195 | 1.5543 | 0.0000 | 0.0000 | 0.1934 | 0.0601 | 4 | 0.0220 | 19.2140 | 79.4760 | 4 | 0.5000 |
| `student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0301 | 0.3763 | 0.1673 | 0.1532 | 1.5510 | 0.0000 | 0.0000 | 0.1819 | 0.0166 | 14 | 0.0203 | 27.0667 | 72.9333 | 13 | 0.9231 |
| `student` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3514 | 0.1641 | 0.1532 | 1.5440 | 0.0000 | 0.0000 | 0.1834 | 0.0160 | 16 | 0.0131 | 22.8000 | 77.2000 | 13 | 0.9231 |
| `student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0289 | 0.3616 | 0.1830 | 0.1532 | 1.5567 | 0.0000 | 0.0000 | 0.1815 | 0.0162 | 14 | 0.0230 | 27.4667 | 72.5333 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 5 | 2 | 3 | 518.8000 | 115 | 750 | 0.9145 | 0.0732 | 0.4365 | 0.0948 | 0.0000 | 0.0000 | 0.0328 | 9.6000 | 0.0157 | 21.7442 | 77.8198 | 8.2000 | 0.6492 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
