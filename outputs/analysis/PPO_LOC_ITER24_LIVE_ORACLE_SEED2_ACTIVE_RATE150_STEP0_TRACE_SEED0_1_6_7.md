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
seeds: `[0, 1, 6, 7]`
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
trace_seeds: `[0, 1, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 638 | `fall_or_nan` | 0.0015 | 0.0190 | 0.1650 | 0.0788 | 1.5193 | 0.0000 | 0.0000 | 0.1782 | 0.0354 | 12 | 0.0192 | 24.4514 | 75.3918 | 10 | 0.9000 |
| `ppo_step0` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0274 | 0.3428 | 0.1928 | 0.1583 | 1.5284 | 0.0000 | 0.0000 | 0.1817 | 0.0167 | 13 | 0.0281 | 25.4667 | 74.5333 | 13 | 0.9231 |
| `ppo_step0` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 212 | `fall_or_nan` | -0.0633 | -0.7918 | 0.2343 | 0.0724 | 1.5167 | 0.0000 | 0.0000 | 0.1764 | 0.0134 | 2 | 0.0325 | 13.6792 | 86.3208 | 3 | 0.6667 |
| `ppo_step0` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 577 | `fall_or_nan` | 0.0542 | 0.6774 | 0.3193 | 0.0033 | 1.5336 | 0.0000 | 0.0000 | 0.1783 | 0.0600 | 8 | 0.0135 | 23.0503 | 76.2565 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0` | 4 | 3 | 1 | 544.2500 | 212 | 750 | 0.0619 | 0.0049 | 0.2279 | 0.0782 | 0.0000 | 0.0000 | 0.0314 | 8.7500 | 0.0233 | 21.6619 | 78.1256 | 8.5000 | 0.8412 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
