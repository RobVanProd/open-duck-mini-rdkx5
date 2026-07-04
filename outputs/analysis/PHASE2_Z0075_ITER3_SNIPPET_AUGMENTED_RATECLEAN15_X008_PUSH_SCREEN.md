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
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
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
| `phase2_z0075_iter3_snipaug_rateclean15` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 116 | `fall_or_nan` | 0.1733 | 2.1662 | 0.9415 | 0.0105 | 1.5513 | 0.0000 | 0.0000 | 0.1986 | 0.0556 | 1 | 0.0011 | 13.7931 | 84.4828 | 1 | 0.0000 |
| `phase2_z0075_iter3_snipaug_rateclean15` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0322 | 0.4022 | 0.2037 | 0.1532 | 1.5255 | 0.0000 | 0.0000 | 0.1862 | 0.0181 | 16 | 0.0192 | 24.9333 | 75.0667 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase2_z0075_iter3_snipaug_rateclean15` | 2 | 1 | 1 | 433.0000 | 116 | 750 | 1.2842 | 0.1027 | 0.5726 | 0.0818 | 0.0000 | 0.0000 | 0.0368 | 8.5000 | 0.0101 | 19.3632 | 79.7747 | 5.5000 | 0.4500 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
