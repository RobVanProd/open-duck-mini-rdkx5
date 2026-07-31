# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `0.95`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 2, 6]`
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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter13_gain095` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0210 | 0.2621 | 0.1781 | 0.1532 | 1.5041 | 0.0000 | 0.0000 | 0.1733 | 0.0148 | 9 | 0.0124 | 18.0000 | 82.0000 | 12 | 0.9167 |
| `iter13_gain095` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0225 | 0.2818 | 0.1824 | 0.1532 | 1.4954 | 0.0000 | 0.0000 | 0.1736 | 0.0138 | 9 | 0.0210 | 19.7333 | 80.2667 | 13 | 0.9231 |
| `iter13_gain095` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 749 | `fall_or_nan` | -0.0042 | -0.0526 | 0.1965 | 0.0556 | 1.4882 | 0.0000 | 0.0000 | 0.1703 | 0.0365 | 11 | 0.0181 | 18.8251 | 80.9079 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter13_gain095` | 3 | 1 | 2 | 749.6667 | 749 | 750 | 0.1638 | 0.0131 | 0.1857 | 0.1206 | 0.0000 | 0.0000 | 0.0217 | 9.6667 | 0.0172 | 18.8528 | 81.0582 | 12.6667 | 0.9209 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
