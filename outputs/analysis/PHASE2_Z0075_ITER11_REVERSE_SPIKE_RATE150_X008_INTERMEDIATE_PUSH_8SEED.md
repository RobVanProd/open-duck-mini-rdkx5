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
| `iter11_reverse_spike_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 637 | `fall_or_nan` | 0.0550 | 0.6874 | 0.2674 | 0.0225 | 1.5750 | 0.0000 | 0.0000 | 0.1920 | 0.0592 | 13 | 0.0131 | 25.7457 | 73.9403 | 10 | 0.9000 |
| `iter11_reverse_spike_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 340 | `fall_or_nan` | 0.0843 | 1.0537 | 0.4484 | -0.0019 | 1.5621 | 0.0000 | 0.0000 | 0.1928 | 0.0613 | 8 | 0.0097 | 25.8824 | 73.2353 | 6 | 0.6667 |
| `iter11_reverse_spike_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 392 | `fall_or_nan` | 0.0716 | 0.8954 | 0.4218 | -0.0027 | 1.5822 | 0.0000 | 0.0556 | 0.1930 | 0.0220 | 11 | 0.0167 | 25.0000 | 75.0000 | 6 | 0.8333 |
| `iter11_reverse_spike_rate150` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0254 | 0.3169 | 0.1645 | 0.1556 | 1.5756 | 0.0000 | 0.0000 | 0.1861 | 0.0160 | 14 | 0.0162 | 24.6667 | 75.3333 | 13 | 0.9231 |
| `iter11_reverse_spike_rate150` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 335 | `fall_or_nan` | 0.0833 | 1.0414 | 0.4478 | -0.0033 | 1.5930 | 0.0000 | 0.0000 | 0.1881 | 0.0608 | 8 | 0.0119 | 20.5970 | 78.5075 | 5 | 0.8000 |
| `iter11_reverse_spike_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -0.2900 | -3.6256 | 0.0567 | 0.0867 | 1.6332 | 0.0000 | 0.0000 | 0.2248 | 0.0261 | 1 | 0.0044 | 12.7660 | 82.9787 | 0 | NA |
| `iter11_reverse_spike_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0287 | 0.3581 | 0.1934 | 0.1533 | 1.5749 | 0.0000 | 0.0000 | 0.1902 | 0.0171 | 12 | 0.0232 | 26.1333 | 73.8667 | 13 | 0.9231 |
| `iter11_reverse_spike_rate150` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 597 | `fall_or_nan` | 0.0546 | 0.6827 | 0.2854 | 0.0126 | 1.5825 | 0.0000 | 0.0000 | 0.1917 | 0.0591 | 13 | 0.0185 | 23.9531 | 75.8794 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter11_reverse_spike_rate150` | 8 | 6 | 2 | 481.0000 | 47 | 750 | 0.1763 | 0.0141 | 0.2857 | 0.0529 | 0.0000 | 0.0070 | 0.0402 | 10.0000 | 0.0142 | 23.0930 | 76.0927 | 7.6250 | 0.8459 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
