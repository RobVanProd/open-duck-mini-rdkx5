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
seeds: `[0, 1, 2, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
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
| `health_routed_parent` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3512 | 0.1704 | 0.1591 | 1.5614 | 0.0000 | 0.0000 | 0.1819 | 0.0159 | 15 | 0.0236 | 25.3333 | 74.6667 | 12 | 0.9167 |
| `health_routed_parent` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0283 | 0.3536 | 0.1707 | 0.1585 | 1.5436 | 0.0000 | 0.0000 | 0.1872 | 0.0149 | 12 | 0.0263 | 23.8667 | 76.1333 | 13 | 0.9231 |
| `health_routed_parent` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0263 | 0.3284 | 0.1840 | 0.1580 | 1.5452 | 0.0000 | 0.0000 | 0.1881 | 0.0139 | 13 | 0.0224 | 24.4000 | 75.6000 | 13 | 0.9231 |
| `health_routed_parent` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0283 | 0.3542 | 0.2076 | 0.1552 | 1.5360 | 0.0000 | 0.0000 | 0.1914 | 0.0141 | 13 | 0.0233 | 23.6000 | 76.4000 | 13 | 0.9231 |
| `health_routed_parent` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0283 | 0.3536 | 0.1529 | 0.1591 | 1.5490 | 0.0000 | 0.0000 | 0.1848 | 0.0149 | 11 | 0.0187 | 25.3333 | 74.6667 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `health_routed_parent` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.3482 | 0.0279 | 0.1771 | 0.1580 | 0.0000 | 0.0000 | 0.0147 | 12.8000 | 0.0229 | 24.5067 | 75.4933 | 12.2000 | 0.9172 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
