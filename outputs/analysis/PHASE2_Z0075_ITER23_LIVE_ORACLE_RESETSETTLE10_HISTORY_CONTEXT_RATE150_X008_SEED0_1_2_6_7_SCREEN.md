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
| `iter23_live_oracle` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0321 | 0.4012 | 0.1719 | 0.1587 | 1.5480 | 0.0000 | 0.0000 | 0.1827 | 0.0142 | 16 | 0.0225 | 25.4667 | 74.5333 | 12 | 0.9167 |
| `iter23_live_oracle` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0284 | 0.3544 | 0.1913 | 0.1561 | 1.5485 | 0.0000 | 0.0000 | 0.1840 | 0.0160 | 16 | 0.0175 | 25.7333 | 74.2667 | 13 | 0.9231 |
| `iter23_live_oracle` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 282 | `fall_or_nan` | -0.0441 | -0.5509 | 0.1832 | 0.0646 | 1.5665 | 0.0000 | 0.0000 | 0.1771 | 0.0145 | 6 | 0.0225 | 21.9858 | 78.0142 | 4 | 0.7500 |
| `iter23_live_oracle` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0265 | 0.3311 | 0.1714 | 0.1577 | 1.5444 | 0.0000 | 0.0000 | 0.1787 | 0.0152 | 15 | 0.0207 | 23.7333 | 76.2667 | 13 | 0.9231 |
| `iter23_live_oracle` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0278 | 0.3479 | 0.1777 | 0.1589 | 1.5429 | 0.0000 | 0.0000 | 0.1816 | 0.0180 | 16 | 0.0234 | 25.3333 | 74.6667 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter23_live_oracle` | 5 | 1 | 4 | 656.4000 | 282 | 750 | 0.1767 | 0.0141 | 0.1791 | 0.1392 | 0.0000 | 0.0000 | 0.0156 | 13.8000 | 0.0213 | 24.4505 | 75.5495 | 10.4000 | 0.8826 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
