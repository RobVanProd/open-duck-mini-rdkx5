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
| `iter14_gain095_seed0_pass_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 107 | `fall_or_nan` | 0.1813 | 2.2667 | 1.0269 | 0.0144 | 1.5881 | 0.0000 | 0.0000 | 0.1939 | 0.0587 | 1 | 0.0015 | 10.2804 | 88.7850 | 1 | 0.0000 |
| `iter14_gain095_seed0_pass_rate150` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0305 | 0.3815 | 0.1981 | 0.1533 | 1.5663 | 0.0000 | 0.0000 | 0.1804 | 0.0203 | 18 | 0.0164 | 27.0667 | 72.9333 | 13 | 0.9231 |
| `iter14_gain095_seed0_pass_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0308 | 0.3846 | 0.1623 | 0.1533 | 1.5761 | 0.0000 | 0.0000 | 0.1796 | 0.0126 | 9 | 0.0195 | 26.2667 | 73.7333 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter14_gain095_seed0_pass_rate150` | 3 | 1 | 2 | 535.6667 | 107 | 750 | 1.0109 | 0.0809 | 0.4625 | 0.1070 | 0.0000 | 0.0000 | 0.0306 | 9.3333 | 0.0125 | 21.2046 | 78.4839 | 9.0000 | 0.6154 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
