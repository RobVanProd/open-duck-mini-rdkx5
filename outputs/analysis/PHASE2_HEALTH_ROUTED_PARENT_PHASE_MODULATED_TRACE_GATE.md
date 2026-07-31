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
| `phase_mod_parent` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0217 | 0.2716 | 0.1994 | 0.1573 | 1.5626 | 0.0000 | 0.0000 | 0.1865 | 0.0197 | 9 | 0.0165 | 21.8667 | 78.1333 | 12 | 0.9167 |
| `phase_mod_parent` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0258 | 0.3230 | 0.2077 | 0.1554 | 1.5578 | 0.0000 | 0.0000 | 0.1872 | 0.0202 | 14 | 0.0193 | 22.6667 | 77.3333 | 13 | 1.0000 |
| `phase_mod_parent` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0263 | 0.3285 | 0.1764 | 0.1592 | 1.5579 | 0.0000 | 0.0000 | 0.1857 | 0.0180 | 14 | 0.0197 | 24.0000 | 76.0000 | 13 | 0.9231 |
| `phase_mod_parent` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0241 | 0.3009 | 0.1850 | 0.1572 | 1.5643 | 0.0000 | 0.0000 | 0.1868 | 0.0166 | 13 | 0.0229 | 22.9333 | 77.0667 | 13 | 0.9231 |
| `phase_mod_parent` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 300 | `fall_or_nan` | -0.0419 | -0.5236 | 0.1780 | 0.0673 | 1.5550 | 0.0000 | 0.0000 | 0.1731 | 0.0351 | 7 | 0.0170 | 18.0000 | 81.3333 | 4 | 0.7500 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_parent` | 5 | 1 | 4 | 660.0000 | 300 | 750 | 0.1401 | 0.0112 | 0.1893 | 0.1393 | 0.0000 | 0.0000 | 0.0219 | 11.4000 | 0.0191 | 21.8933 | 77.9733 | 11.0000 | 0.9026 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
