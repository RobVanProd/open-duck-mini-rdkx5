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
seeds: `[0, 5, 7]`
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
| `full8_mlp_router_live_corrected_iter2` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0252 | 0.3149 | 0.1941 | 0.1588 | 1.5829 | 0.0000 | 0.0000 | 0.1840 | 0.0165 | 10 | 0.0309 | 23.8667 | 76.1333 | 12 | 0.9167 |
| `full8_mlp_router_live_corrected_iter2` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 169 | `fall_or_nan` | 0.1257 | 1.5711 | 0.7670 | 0.0100 | 1.5940 | 0.0000 | 0.0000 | 0.2021 | 0.0575 | 2 | 0.0081 | 13.6095 | 85.7988 | 3 | 0.6667 |
| `full8_mlp_router_live_corrected_iter2` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 605 | `fall_or_nan` | 0.0549 | 0.6863 | 0.2476 | 0.0106 | 1.5936 | 0.0000 | 0.0000 | 0.1875 | 0.0594 | 11 | 0.0150 | 24.2975 | 75.5372 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_mlp_router_live_corrected_iter2` | 3 | 2 | 1 | 508.0000 | 169 | 750 | 0.8574 | 0.0686 | 0.4029 | 0.0598 | 0.0000 | 0.0000 | 0.0444 | 7.6667 | 0.0180 | 20.5912 | 79.1564 | 7.6667 | 0.8194 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
