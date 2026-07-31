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
| `seed7_weighted_student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0272 | 0.3403 | 0.1737 | 0.1581 | 1.5956 | 0.0000 | 0.0000 | 0.1859 | 0.0170 | 15 | 0.0180 | 22.0000 | 78.0000 | 12 | 0.9167 |
| `seed7_weighted_student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0254 | 0.3170 | 0.1876 | 0.1581 | 1.6031 | 0.0000 | 0.0000 | 0.1907 | 0.0164 | 13 | 0.0215 | 23.2000 | 76.8000 | 13 | 1.0000 |
| `seed7_weighted_student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0269 | 0.3367 | 0.1894 | 0.1581 | 1.5916 | 0.0000 | 0.0000 | 0.1888 | 0.0168 | 12 | 0.0206 | 23.6000 | 76.4000 | 13 | 0.9231 |
| `seed7_weighted_student` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0232 | 0.2896 | 0.1917 | 0.1581 | 1.5935 | 0.0000 | 0.0000 | 0.1868 | 0.0142 | 12 | 0.0223 | 22.9333 | 77.0667 | 13 | 0.9231 |
| `seed7_weighted_student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0265 | 0.3311 | 0.1724 | 0.1581 | 1.6066 | 0.0000 | 0.0000 | 0.1895 | 0.0141 | 11 | 0.0223 | 24.6667 | 75.3333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed7_weighted_student` | 5 | 0 | 5 | 750.0000 | 750 | 750 | 0.3230 | 0.0258 | 0.1830 | 0.1581 | 0.0000 | 0.0000 | 0.0157 | 12.6000 | 0.0209 | 23.2800 | 76.7200 | 12.2000 | 0.9526 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
