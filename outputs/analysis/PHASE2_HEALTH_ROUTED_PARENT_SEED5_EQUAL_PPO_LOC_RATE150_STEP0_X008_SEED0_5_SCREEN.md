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
seeds: `[0, 5]`
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
| `ppo_step0_seed5_equal` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0275 | 0.3437 | 0.1692 | 0.1590 | 1.5158 | 0.0000 | 0.0000 | 0.1857 | 0.0165 | 13 | 0.0228 | 23.4667 | 76.5333 | 12 | 0.9167 |
| `ppo_step0_seed5_equal` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0259 | 0.3241 | 0.1809 | 0.1586 | 1.5115 | 0.0000 | 0.0000 | 0.1848 | 0.0129 | 12 | 0.0253 | 22.4000 | 77.6000 | 13 | 0.9231 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0_seed5_equal` | 2 | 0 | 2 | 750.0000 | 750 | 750 | 0.3339 | 0.0267 | 0.1751 | 0.1588 | 0.0000 | 0.0000 | 0.0147 | 12.5000 | 0.0241 | 22.9333 | 77.0667 | 12.5000 | 0.9199 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
