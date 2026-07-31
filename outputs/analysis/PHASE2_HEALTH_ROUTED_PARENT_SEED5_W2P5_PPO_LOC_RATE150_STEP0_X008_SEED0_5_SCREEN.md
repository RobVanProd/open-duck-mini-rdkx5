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
seeds: `[0, 5]`
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
| `ppo_step0_seed5_w2p5` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 658 | `fall_or_nan` | -0.0004 | -0.0048 | 0.1713 | 0.0640 | 1.5419 | 0.0000 | 0.4312 | 0.1805 | 0.0356 | 11 | 0.0154 | 24.4681 | 75.3799 | 10 | 0.9000 |
| `ppo_step0_seed5_w2p5` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0303 | 0.3785 | 0.1716 | 0.1582 | 1.5423 | 0.0000 | 0.0000 | 0.1862 | 0.0134 | 12 | 0.0254 | 26.1333 | 73.8667 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0_seed5_w2p5` | 2 | 1 | 1 | 704.0000 | 658 | 750 | 0.1868 | 0.0149 | 0.1714 | 0.1111 | 0.0000 | 0.2156 | 0.0245 | 11.5000 | 0.0204 | 25.3007 | 74.6233 | 11.5000 | 0.9115 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
