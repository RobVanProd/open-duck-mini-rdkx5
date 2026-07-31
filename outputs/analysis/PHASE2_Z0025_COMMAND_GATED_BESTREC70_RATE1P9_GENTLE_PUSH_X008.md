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
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0025`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0289 | 0.3617 | 0.1228 | 0.1519 | 1.9095 | 0.0000 | 0.0000 | 0.1967 | 0.0123 | 14 | 0.0208 | 20.8000 | 79.2000 | 12 | 0.9167 |
| `gated` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0323 | 0.4033 | 0.1301 | 0.1563 | 1.9214 | 0.0000 | 0.0119 | 0.1935 | 0.0137 | 11 | 0.0181 | 24.9333 | 74.9333 | 13 | 1.0000 |
| `gated` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0309 | 0.3856 | 0.1164 | 0.1512 | 1.9176 | 0.0000 | 0.0000 | 0.1953 | 0.0117 | 9 | 0.0164 | 22.2667 | 77.7333 | 13 | 0.9231 |
| `gated` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0281 | 0.3515 | 0.1302 | 0.1547 | 1.9162 | 0.0000 | 0.0582 | 0.1924 | 0.0115 | 13 | 0.0137 | 20.8000 | 79.2000 | 13 | 1.0000 |
| `gated` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0341 | 0.4258 | 0.1092 | 0.1506 | 1.9163 | 0.0000 | 0.0063 | 0.1903 | 0.0119 | 14 | 0.0061 | 24.2667 | 75.7333 | 12 | 1.0000 |
| `gated` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0307 | 0.3834 | 0.1201 | 0.1464 | 1.9142 | 0.0000 | 0.0000 | 0.1939 | 0.0184 | 19 | 0.0086 | 21.7333 | 78.0000 | 13 | 1.0000 |
| `gated` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0298 | 0.3721 | 0.1179 | 0.1531 | 1.9087 | 0.0000 | 0.0000 | 0.1916 | 0.0180 | 17 | 0.0048 | 23.0667 | 76.9333 | 13 | 0.9231 |
| `gated` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0282 | 0.3528 | 0.1193 | 0.1564 | 1.9208 | 0.0000 | 0.0414 | 0.1929 | 0.0124 | 10 | 0.0134 | 20.8000 | 79.2000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3795 | 0.0304 | 0.1208 | 0.1526 | 0.0000 | 0.0147 | 0.0137 | 13.3750 | 0.0127 | 22.3333 | 77.6167 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
