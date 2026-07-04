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
| `iter12_pass_control_reverse_soft_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 690 | `fall_or_nan` | 0.0529 | 0.6608 | 0.3025 | 0.0184 | 1.5577 | 0.0000 | 0.0000 | 0.1905 | 0.0552 | 12 | 0.0250 | 23.6232 | 76.0870 | 11 | 0.9091 |
| `iter12_pass_control_reverse_soft_rate150` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 546 | `fall_or_nan` | 0.0627 | 0.7842 | 0.3046 | 0.0064 | 1.5488 | 0.0000 | 0.2696 | 0.1910 | 0.0614 | 13 | 0.0151 | 30.2198 | 69.5971 | 9 | 0.8889 |
| `iter12_pass_control_reverse_soft_rate150` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 153 | `fall_or_nan` | 0.1386 | 1.7330 | 0.8505 | 0.0050 | 1.5342 | 0.0000 | 0.0000 | 0.2091 | 0.0543 | 3 | 0.0054 | 20.9150 | 79.0850 | 2 | 0.5000 |
| `iter12_pass_control_reverse_soft_rate150` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 444 | `fall_or_nan` | -0.0224 | -0.2795 | 0.1812 | 0.0726 | 1.5901 | 0.0000 | 0.0000 | 0.1825 | 0.0314 | 9 | 0.0270 | 21.3964 | 78.3784 | 8 | 0.7500 |
| `iter12_pass_control_reverse_soft_rate150` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 311 | `fall_or_nan` | 0.0845 | 1.0557 | 0.5090 | 0.0031 | 1.5720 | 0.0000 | 0.0873 | 0.1876 | 0.0620 | 3 | 0.0041 | 20.2572 | 79.0997 | 5 | 0.8000 |
| `iter12_pass_control_reverse_soft_rate150` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | `fall_or_nan` | -0.3125 | -3.9058 | 0.0561 | 0.0708 | 1.6083 | 0.0000 | 0.0000 | 0.2223 | 0.0260 | 2 | 0.0082 | 12.7660 | 78.7234 | 0 | NA |
| `iter12_pass_control_reverse_soft_rate150` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 685 | `fall_or_nan` | 0.0516 | 0.6455 | 0.2802 | 0.0196 | 1.5614 | 0.0000 | 0.0000 | 0.1873 | 0.0597 | 13 | 0.0166 | 24.8175 | 75.0365 | 12 | 0.9167 |
| `iter12_pass_control_reverse_soft_rate150` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 475 | `fall_or_nan` | 0.0630 | 0.7873 | 0.3284 | 0.0161 | 1.5630 | 0.0000 | 0.0000 | 0.1934 | 0.0437 | 10 | 0.0151 | 25.6842 | 74.3158 | 6 | 0.8333 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter12_pass_control_reverse_soft_rate150` | 8 | 8 | 0 | 418.8750 | 47 | 690 | 0.1851 | 0.0148 | 0.3516 | 0.0265 | 0.0000 | 0.0446 | 0.0492 | 8.1250 | 0.0146 | 22.4599 | 76.2903 | 6.6250 | 0.7997 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
