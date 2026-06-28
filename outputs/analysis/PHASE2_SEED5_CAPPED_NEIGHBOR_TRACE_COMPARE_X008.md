# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[4, 5, 6]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[4, 5, 6]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_capped` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0356 | 0.4445 | 0.0961 | 0.1506 | 2.4347 | 0.0000 | 0.1960 | 0.0108 | 4 | 0.0067 | 21.6000 | 78.4000 | 0 | NA |
| `seed5_capped` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 55 | `fall_or_nan` | -0.2492 | -3.1144 | 0.0691 | 0.0819 | 3.2094 | 0.2094 | 0.2049 | 0.0317 | 2 | 0.0069 | 7.2727 | 81.8182 | 0 | NA |
| `seed5_capped` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0357 | 0.4468 | 0.1014 | 0.1532 | 2.4606 | 0.0000 | 0.1993 | 0.0192 | 6 | 0.0093 | 26.0000 | 74.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_capped` | 3 | 1 | 2 | 185.0000 | 55 | 250 | -0.7410 | -0.0593 | 0.0889 | 0.1286 | 0.0698 | 0.0206 | 4.0000 | 0.0076 | 18.2909 | 78.0727 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
