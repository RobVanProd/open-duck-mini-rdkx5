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
| `iter27` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0272 | 0.3395 | 0.1793 | 0.1587 | 1.5389 | 0.0000 | 0.0000 | 0.1848 | 0.0151 | 14 | 0.0187 | 25.8667 | 74.1333 | 12 | 0.9167 |
| `iter27` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3830 | 0.1897 | 0.1576 | 1.5272 | 0.0000 | 0.0000 | 0.1843 | 0.0123 | 12 | 0.0261 | 27.2000 | 72.8000 | 13 | 0.9231 |
| `iter27` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 307 | `fall_or_nan` | -0.0386 | -0.4823 | 0.1841 | 0.0701 | 1.5546 | 0.0000 | 0.0000 | 0.1753 | 0.0341 | 6 | 0.0228 | 20.1954 | 79.8046 | 5 | 0.8000 |
| `iter27` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 390 | `fall_or_nan` | 0.0776 | 0.9697 | 0.4099 | 0.0005 | 1.5506 | 0.0000 | 0.0000 | 0.1868 | 0.0578 | 8 | 0.0295 | 27.1795 | 72.5641 | 6 | 0.8333 |
| `iter27` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 611 | `fall_or_nan` | 0.0011 | 0.0141 | 0.2035 | 0.0817 | 1.5395 | 0.0000 | 0.0000 | 0.1827 | 0.0354 | 13 | 0.0228 | 27.9869 | 71.6858 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter27` | 5 | 3 | 2 | 561.6000 | 307 | 750 | 0.2448 | 0.0196 | 0.2333 | 0.0937 | 0.0000 | 0.0000 | 0.0309 | 10.6000 | 0.0240 | 25.6857 | 74.1976 | 8.8000 | 0.8696 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
