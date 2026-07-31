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
| `history_context` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0279 | 0.3483 | 0.1735 | 0.1590 | 1.5596 | 0.0000 | 0.0000 | 0.1793 | 0.0141 | 13 | 0.0183 | 26.0000 | 74.0000 | 12 | 0.9167 |
| `history_context` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0252 | 0.3144 | 0.1825 | 0.1573 | 1.5518 | 0.0000 | 0.0000 | 0.1849 | 0.0146 | 13 | 0.0205 | 23.2000 | 76.8000 | 13 | 0.9231 |
| `history_context` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0303 | 0.3787 | 0.1780 | 0.1590 | 1.5423 | 0.0000 | 0.0000 | 0.1842 | 0.0151 | 17 | 0.0220 | 25.3333 | 74.6667 | 13 | 0.9231 |
| `history_context` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0237 | 0.2961 | 0.1765 | 0.1584 | 1.5505 | 0.0000 | 0.0000 | 0.1801 | 0.0135 | 13 | 0.0189 | 22.0000 | 78.0000 | 13 | 0.9231 |
| `history_context` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 274 | `fall_or_nan` | -0.0417 | -0.5217 | 0.1734 | 0.0690 | 1.5707 | 0.0000 | 0.0000 | 0.1767 | 0.0357 | 7 | 0.0269 | 20.4380 | 78.4672 | 3 | 0.6667 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `history_context` | 5 | 1 | 4 | 654.8000 | 274 | 750 | 0.1632 | 0.0131 | 0.1768 | 0.1405 | 0.0000 | 0.0000 | 0.0186 | 12.6000 | 0.0213 | 23.3943 | 76.3868 | 10.8000 | 0.8705 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
