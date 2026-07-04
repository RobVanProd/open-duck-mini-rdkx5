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
seeds: `[1, 2, 3, 5, 6]`
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
trace_seeds: `[1, 2, 3, 5, 6]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter10_spike_local_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 419 | `fall_or_nan` | -0.0112 | -0.1401 | 0.1649 | 0.0836 | 1.5598 | 0.0000 | 0.0000 | 0.1803 | 0.0345 | 10 | 0.0102 | 29.5943 | 69.4511 | 7 | 0.8571 |
| `iter10_spike_local_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 714 | `fall_or_nan` | 0.0525 | 0.6560 | 0.2694 | 0.0104 | 1.5607 | 0.0000 | 0.2900 | 0.1869 | 0.0637 | 12 | 0.0178 | 24.9300 | 74.9300 | 12 | 0.9167 |
| `iter10_spike_local_rate150` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 527 | `fall_or_nan` | 0.0557 | 0.6962 | 0.3261 | 0.0040 | 1.5461 | 0.0000 | 0.0000 | 0.1833 | 0.0624 | 10 | 0.0064 | 24.4782 | 75.1423 | 9 | 0.8889 |
| `iter10_spike_local_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 45 | `fall_or_nan` | -0.2996 | -3.7453 | 0.0581 | 0.0888 | 1.5059 | 0.0000 | 0.0000 | 0.2203 | 0.0225 | 1 | 0.0079 | 17.7778 | 80.0000 | 0 | NA |
| `iter10_spike_local_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 611 | `fall_or_nan` | 0.0526 | 0.6569 | 0.2898 | 0.0031 | 1.5653 | 0.0000 | 0.1897 | 0.1804 | 0.0605 | 8 | 0.0167 | 22.5859 | 77.0867 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter10_spike_local_rate150` | 5 | 5 | 0 | 463.2000 | 45 | 714 | -0.3752 | -0.0300 | 0.2217 | 0.0380 | 0.0000 | 0.0959 | 0.0487 | 8.2000 | 0.0118 | 23.8732 | 75.3220 | 7.6000 | 0.8907 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
