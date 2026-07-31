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
eval_push_magnitude: `0.1`-`0.2`
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
| `limited` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3515 | 0.1445 | 0.1519 | 1.9050 | 0.0000 | 0.0000 | 0.1953 | 0.0140 | 12 | 0.0190 | 20.6667 | 79.3333 | 12 | 0.9167 |
| `limited` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0308 | 0.3854 | 0.1497 | 0.1563 | 1.9161 | 0.0000 | 0.0000 | 0.1963 | 0.0136 | 14 | 0.0150 | 23.3333 | 76.5333 | 13 | 1.0000 |
| `limited` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0309 | 0.3862 | 0.1278 | 0.1512 | 1.9161 | 0.0000 | 0.0000 | 0.1903 | 0.0140 | 17 | 0.0194 | 24.8000 | 75.2000 | 13 | 0.9231 |
| `limited` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0311 | 0.3882 | 0.1638 | 0.1547 | 1.9085 | 0.0000 | 0.0000 | 0.1917 | 0.0140 | 15 | 0.0191 | 25.6000 | 74.4000 | 13 | 1.0000 |
| `limited` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0318 | 0.3970 | 0.1252 | 0.1506 | 1.9203 | 0.0000 | 0.0000 | 0.1929 | 0.0115 | 9 | 0.0231 | 23.4667 | 76.5333 | 12 | 1.0000 |
| `limited` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0310 | 0.3869 | 0.1218 | 0.1464 | 1.9157 | 0.0000 | 0.0000 | 0.1932 | 0.0182 | 16 | 0.0089 | 21.6000 | 78.1333 | 13 | 1.0000 |
| `limited` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0317 | 0.3969 | 0.1501 | 0.1531 | 1.9093 | 0.0000 | 0.0000 | 0.1977 | 0.0184 | 16 | 0.0141 | 24.5333 | 75.4667 | 13 | 0.9231 |
| `limited` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0292 | 0.3647 | 0.1205 | 0.1565 | 1.9147 | 0.0000 | 0.0000 | 0.1938 | 0.0118 | 11 | 0.0115 | 22.5333 | 77.4667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3821 | 0.0306 | 0.1379 | 0.1526 | 0.0000 | 0.0000 | 0.0144 | 13.7500 | 0.0163 | 23.3167 | 76.6333 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
