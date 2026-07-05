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
| `full8_mlp_router_seed0_seed5_startup_cost_wide` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0268 | 0.3348 | 0.1668 | 0.1591 | 1.5866 | 0.0000 | 0.0000 | 0.1850 | 0.0158 | 13 | 0.0170 | 23.2000 | 76.8000 | 12 | 0.9167 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 161 | `fall_or_nan` | 0.1296 | 1.6196 | 0.8511 | 0.0132 | 1.5933 | 0.0000 | 0.0000 | 0.1981 | 0.0608 | 2 | 0.0096 | 10.5590 | 87.5776 | 2 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0254 | 0.3178 | 0.1914 | 0.1572 | 1.5885 | 0.0000 | 0.0000 | 0.1918 | 0.0142 | 15 | 0.0188 | 22.4000 | 77.6000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_mlp_router_seed0_seed5_startup_cost_wide` | 3 | 1 | 2 | 553.6667 | 161 | 750 | 0.7574 | 0.0606 | 0.4031 | 0.1099 | 0.0000 | 0.0000 | 0.0303 | 10.0000 | 0.0151 | 18.7197 | 80.6592 | 8.0000 | 0.9722 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
