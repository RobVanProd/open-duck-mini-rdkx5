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
push_recovery_window_s: `0.5`
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
| `full8_router_tneg1p8_phase_contact` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 155 | `fall_or_nan` | 0.1286 | 1.6078 | 0.8012 | 0.0158 | 1.5827 | 0.0000 | 0.4199 | 0.1964 | 0.0604 | 2 | 0.0034 | 12.2581 | 86.4516 | 2 | 1.0000 |
| `full8_router_tneg1p8_phase_contact` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0279 | 0.3482 | 0.1823 | 0.1572 | 1.5838 | 0.0000 | 0.0000 | 0.1872 | 0.0136 | 15 | 0.0263 | 23.2000 | 76.8000 | 13 | 1.0000 |
| `full8_router_tneg1p8_phase_contact` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3563 | 0.1738 | 0.1589 | 1.5674 | 0.0000 | 0.0000 | 0.1835 | 0.0157 | 15 | 0.0260 | 26.2667 | 73.7333 | 13 | 0.9231 |
| `full8_router_tneg1p8_phase_contact` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 149 | `fall_or_nan` | 0.1390 | 1.7375 | 0.8611 | 0.0101 | 1.5932 | 0.0000 | 0.0000 | 0.1955 | 0.0537 | 1 | 0.0022 | 16.1074 | 83.8926 | 2 | 1.0000 |
| `full8_router_tneg1p8_phase_contact` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 191 | `fall_or_nan` | 0.1189 | 1.4861 | 0.7697 | -0.0050 | 1.5809 | 0.0000 | 0.1226 | 0.1970 | 0.0591 | 2 | 0.0071 | 14.6597 | 84.8168 | 3 | 0.6667 |
| `full8_router_tneg1p8_phase_contact` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 150 | `fall_or_nan` | 0.1407 | 1.7586 | 0.8722 | 0.0033 | 1.5769 | 0.0000 | 0.3500 | 0.1987 | 0.0584 | 1 | 0.0022 | 12.0000 | 86.6667 | 2 | 1.0000 |
| `full8_router_tneg1p8_phase_contact` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 563 | `fall_or_nan` | -0.0075 | -0.0941 | 0.1822 | 0.0730 | 1.5827 | 0.0000 | 0.0000 | 0.1791 | 0.0333 | 10 | 0.0221 | 21.6696 | 78.1528 | 10 | 0.9000 |
| `full8_router_tneg1p8_phase_contact` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3512 | 0.1710 | 0.1589 | 1.5757 | 0.0000 | 0.0000 | 0.1850 | 0.0135 | 14 | 0.0182 | 26.0000 | 74.0000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_router_tneg1p8_phase_contact` | 8 | 5 | 3 | 432.2500 | 149 | 750 | 0.9440 | 0.0755 | 0.5017 | 0.0715 | 0.0000 | 0.1116 | 0.0385 | 7.5000 | 0.0134 | 19.0202 | 80.5642 | 6.8750 | 0.9362 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
