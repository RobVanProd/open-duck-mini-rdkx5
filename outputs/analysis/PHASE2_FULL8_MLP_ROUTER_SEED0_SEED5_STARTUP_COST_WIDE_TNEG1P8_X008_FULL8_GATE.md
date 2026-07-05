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
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0267 | 0.3338 | 0.1708 | 0.1590 | 1.5735 | 0.0000 | 0.0000 | 0.1884 | 0.0167 | 13 | 0.0206 | 22.6667 | 77.3333 | 12 | 0.9167 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0280 | 0.3502 | 0.2022 | 0.1559 | 1.5711 | 0.0000 | 0.0000 | 0.1893 | 0.0196 | 16 | 0.0321 | 25.4667 | 74.5333 | 13 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0284 | 0.3556 | 0.1798 | 0.1584 | 1.5853 | 0.0000 | 0.0000 | 0.1843 | 0.0154 | 14 | 0.0186 | 26.8000 | 73.2000 | 13 | 0.9231 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0246 | 0.3077 | 0.1780 | 0.1585 | 1.5824 | 0.0000 | 0.0000 | 0.1852 | 0.0145 | 12 | 0.0231 | 23.2000 | 76.8000 | 13 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0275 | 0.3436 | 0.2069 | 0.1583 | 1.5900 | 0.0000 | 0.0000 | 0.1902 | 0.0167 | 9 | 0.0207 | 22.8000 | 77.2000 | 12 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0303 | 0.3788 | 0.1810 | 0.1583 | 1.5601 | 0.0000 | 0.0000 | 0.1881 | 0.0144 | 17 | 0.0246 | 26.6667 | 73.3333 | 13 | 1.0000 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0267 | 0.3333 | 0.1927 | 0.1563 | 1.5745 | 0.0000 | 0.0000 | 0.1922 | 0.0142 | 16 | 0.0247 | 24.6667 | 75.3333 | 13 | 0.9231 |
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0289 | 0.3614 | 0.1753 | 0.1591 | 1.5764 | 0.0000 | 0.0000 | 0.1893 | 0.0152 | 18 | 0.0219 | 23.4667 | 76.5333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full8_mlp_router_seed0_seed5_startup_cost_wide_tneg1p8` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3456 | 0.0276 | 0.1859 | 0.1580 | 0.0000 | 0.0000 | 0.0158 | 14.3750 | 0.0233 | 24.4667 | 75.5333 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
