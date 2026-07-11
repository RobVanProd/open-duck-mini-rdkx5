# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `1.0`
seeds: `[9, 12, 14, 19, 20, 36, 37]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `None`
reset_settle_ticks: `10`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[9, 12, 14, 19, 20, 36, 37]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `settle10` | 9 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 22 | `fall_or_nan` | -0.6099 | -7.6234 | 0.3228 | 0.0747 | 1.2680 | 0.0000 | 0.0000 | 0.1233 | 0.0200 | 1 | 0.0058 | 18.1818 | 77.2727 | 0 | NA |
| `settle10` | 12 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 25 | `fall_or_nan` | -0.5730 | -7.1623 | 0.2806 | 0.0681 | 1.2304 | 0.0000 | 0.0000 | 0.1340 | 0.0246 | 1 | 0.0099 | 24.0000 | 64.0000 | 0 | NA |
| `settle10` | 14 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.0520 | -0.6500 | 0.1843 | 0.0888 | 1.6790 | 0.0000 | 0.0000 | 0.1904 | 0.0120 | 0 | 0.0000 | 96.9697 | 0.0000 | 0 | NA |
| `settle10` | 19 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 24 | `fall_or_nan` | -0.0457 | -0.5714 | 0.2106 | 0.0762 | 1.2499 | 0.0000 | 0.0000 | 0.1729 | 0.0081 | 1 | 0.0122 | 91.6667 | 0.0000 | 0 | NA |
| `settle10` | 20 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 19 | `fall_or_nan` | -0.0400 | -0.5003 | 0.4053 | 0.0661 | 1.1076 | 0.0000 | 0.0000 | 0.1514 | 0.0041 | 0 | 0.0000 | 89.4737 | 0.0000 | 0 | NA |
| `settle10` | 36 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 16 | `fall_or_nan` | -0.2153 | -2.6908 | 0.0827 | 0.1250 | 1.5696 | 0.0000 | 0.0000 | 0.1416 | 0.0147 | 0 | 0.0000 | 93.7500 | 0.0000 | 0 | NA |
| `settle10` | 37 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 20 | `fall_or_nan` | -0.0792 | -0.9898 | 0.2217 | 0.0666 | 1.5338 | 0.0000 | 0.0000 | 0.1695 | 0.0046 | 0 | 0.0000 | 95.0000 | 0.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `settle10` | 7 | 7 | 0 | 22.7143 | 16 | 33 | -2.8840 | -0.2307 | 0.2440 | 0.0808 | 0.0000 | 0.0000 | 0.0126 | 0.4286 | 0.0040 | 72.7203 | 20.1818 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
