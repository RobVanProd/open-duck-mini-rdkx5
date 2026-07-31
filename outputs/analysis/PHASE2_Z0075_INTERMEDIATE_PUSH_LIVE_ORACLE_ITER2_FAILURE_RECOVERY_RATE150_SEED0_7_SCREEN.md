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
seeds: `[0, 7]`
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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter2_recovery_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 689 | `fall_or_nan` | 0.0582 | 0.7277 | 0.2831 | 0.0182 | 1.5745 | 0.0000 | 0.0638 | 0.1954 | 0.0590 | 17 | 0.0141 | 28.4470 | 71.4078 | 11 | 0.9091 |
| `iter2_recovery_rate150` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0300 | 0.3747 | 0.1976 | 0.1568 | 1.5750 | 0.0000 | 0.0000 | 0.1873 | 0.0156 | 20 | 0.0174 | 26.6667 | 73.3333 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter2_recovery_rate150` | 2 | 1 | 1 | 719.5000 | 689 | 750 | 0.5512 | 0.0441 | 0.2404 | 0.0875 | 0.0000 | 0.0319 | 0.0373 | 18.5000 | 0.0158 | 27.5568 | 72.3706 | 10.5000 | 0.9045 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
