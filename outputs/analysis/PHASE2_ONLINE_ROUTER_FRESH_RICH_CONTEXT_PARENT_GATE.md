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
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rich_context_parent` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0232 | 0.2897 | 0.1661 | 0.1591 | 1.5451 | 0.0000 | 0.0000 | 0.1808 | 0.0166 | 9 | 0.0248 | 19.4667 | 80.5333 | 12 | 0.9167 |
| `rich_context_parent` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 161 | `fall_or_nan` | 0.1382 | 1.7276 | 0.9036 | -0.0090 | 1.5505 | 0.0000 | 0.0000 | 0.2000 | 0.0621 | 3 | 0.0136 | 14.2857 | 84.4720 | 2 | 1.0000 |
| `rich_context_parent` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0238 | 0.2972 | 0.1763 | 0.1569 | 1.5585 | 0.0000 | 0.0000 | 0.1835 | 0.0153 | 11 | 0.0184 | 21.7333 | 78.2667 | 13 | 0.9231 |
| `rich_context_parent` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0253 | 0.3158 | 0.1811 | 0.1575 | 1.5443 | 0.0000 | 0.0000 | 0.1871 | 0.0152 | 11 | 0.0239 | 23.0667 | 76.9333 | 13 | 0.9231 |
| `rich_context_parent` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3302 | 0.1775 | 0.1589 | 1.5559 | 0.0000 | 0.0000 | 0.1835 | 0.0138 | 13 | 0.0203 | 24.6667 | 75.3333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rich_context_parent` | 5 | 1 | 4 | 632.2000 | 161 | 750 | 0.5921 | 0.0474 | 0.3209 | 0.1247 | 0.0000 | 0.0000 | 0.0246 | 9.4000 | 0.0202 | 20.6438 | 79.1077 | 10.0000 | 0.9526 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
