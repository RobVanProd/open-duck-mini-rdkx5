# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0643 | 0.1613 | 0.0111 | 0.0000 | 0.0000 | 0.0414 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | NA | 0.0678 | 0.1609 | 0.0097 | 0.0000 | 0.0000 | 0.0423 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0008 | NA | 0.0655 | 0.1614 | 0.0095 | 0.0000 | 0.0000 | 0.0415 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0673 | 0.1612 | 0.0094 | 0.0000 | 0.0000 | 0.0422 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0644 | 0.1615 | 0.0092 | 0.0000 | 0.0000 | 0.0416 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0686 | 0.1610 | 0.0093 | 0.0000 | 0.0000 | 0.0433 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0707 | 0.1611 | 0.0123 | 0.0000 | 0.0000 | 0.0424 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | NA | 0.0663 | 0.1613 | 0.0074 | 0.0000 | 0.0000 | 0.0409 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0007 | 0.0669 | 0.1612 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
