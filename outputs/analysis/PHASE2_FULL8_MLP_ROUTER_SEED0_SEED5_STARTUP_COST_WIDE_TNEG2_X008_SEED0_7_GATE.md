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
seeds: `[0, 7]`
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
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 166 | `fall_or_nan` | 0.1265 | 1.5808 | 0.8282 | 0.0083 | 1.5876 | 0.0000 | 0.0000 | 0.1989 | 0.0595 | 3 | 0.0064 | 10.8434 | 87.9518 | 2 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0352 | 0.4396 | 0.1833 | 0.1562 | 1.5716 | 0.0000 | 0.0000 | 0.1894 | 0.0162 | 18 | 0.0186 | 27.6000 | 72.4000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg2` | 2 | 1 | 1 | 458.0000 | 166 | 750 | 1.0102 | 0.0808 | 0.5057 | 0.0822 | 0.0000 | 0.0000 | 0.0379 | 10.5000 | 0.0125 | 19.2217 | 80.1759 | 6.0000 | 1.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
