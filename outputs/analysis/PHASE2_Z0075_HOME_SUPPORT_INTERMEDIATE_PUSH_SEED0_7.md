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
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
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
| `iter10_spike_local_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 114 | `fall_or_nan` | 0.1756 | 2.1946 | 0.9954 | 0.0059 | 1.5890 | 0.0000 | 0.0000 | 0.1950 | 0.0524 | 2 | 0.0053 | 14.0351 | 85.0877 | 1 | 0.0000 |
| `iter10_spike_local_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0300 | 0.3756 | 0.1840 | 0.1532 | 1.5502 | 0.0000 | 0.0000 | 0.1819 | 0.0147 | 13 | 0.0167 | 23.4667 | 76.5333 | 13 | 0.9231 |
| `iter10_spike_local_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 604 | `fall_or_nan` | -0.0023 | -0.0289 | 0.1749 | 0.0821 | 1.5685 | 0.0000 | 0.0000 | 0.1756 | 0.0363 | 14 | 0.0132 | 25.6623 | 74.0066 | 10 | 0.9000 |
| `iter10_spike_local_rate150` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3305 | 0.1685 | 0.1532 | 1.5648 | 0.0000 | 0.0000 | 0.1845 | 0.0130 | 15 | 0.0200 | 24.2667 | 75.7333 | 13 | 0.9231 |
| `iter10_spike_local_rate150` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0293 | 0.3658 | 0.1730 | 0.1532 | 1.5539 | 0.0000 | 0.0000 | 0.1803 | 0.0137 | 13 | 0.0220 | 24.8000 | 75.2000 | 12 | 0.9167 |
| `iter10_spike_local_rate150` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0279 | 0.3485 | 0.1824 | 0.1532 | 1.5420 | 0.0000 | 0.0000 | 0.1879 | 0.0138 | 14 | 0.0206 | 24.4000 | 75.6000 | 13 | 0.9231 |
| `iter10_spike_local_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 672 | `fall_or_nan` | 0.0009 | 0.0114 | 0.1562 | 0.0755 | 1.5578 | 0.0000 | 0.0000 | 0.1764 | 0.0366 | 10 | 0.0129 | 25.0000 | 74.8512 | 12 | 0.8333 |
| `iter10_spike_local_rate150` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0275 | 0.3434 | 0.1860 | 0.1532 | 1.5553 | 0.0000 | 0.0000 | 0.1813 | 0.0161 | 16 | 0.0288 | 25.6000 | 74.4000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter10_spike_local_rate150` | 8 | 3 | 5 | 642.5000 | 114 | 750 | 0.4926 | 0.0394 | 0.2775 | 0.1162 | 0.0000 | 0.0000 | 0.0246 | 12.1250 | 0.0174 | 23.4038 | 76.4265 | 10.5000 | 0.7899 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
