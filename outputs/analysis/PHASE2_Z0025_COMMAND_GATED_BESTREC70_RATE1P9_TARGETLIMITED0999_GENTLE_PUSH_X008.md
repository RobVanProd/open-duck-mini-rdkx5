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
| `limited` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3300 | 0.1285 | 0.1519 | 1.9058 | 0.0000 | 0.0000 | 0.1950 | 0.0124 | 11 | 0.0160 | 20.1333 | 79.8667 | 12 | 0.9167 |
| `limited` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0324 | 0.4044 | 0.1246 | 0.1563 | 1.9198 | 0.0000 | 0.0000 | 0.1929 | 0.0134 | 14 | 0.0196 | 24.8000 | 75.0667 | 13 | 1.0000 |
| `limited` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3826 | 0.1166 | 0.1512 | 1.9229 | 0.0000 | 0.0000 | 0.1936 | 0.0112 | 12 | 0.0082 | 22.5333 | 77.4667 | 13 | 0.9231 |
| `limited` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0279 | 0.3489 | 0.1364 | 0.1547 | 1.9029 | 0.0000 | 0.0000 | 0.1922 | 0.0130 | 13 | 0.0218 | 22.8000 | 77.2000 | 13 | 1.0000 |
| `limited` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0329 | 0.4107 | 0.1093 | 0.1506 | 1.9251 | 0.0000 | 0.0000 | 0.1906 | 0.0120 | 13 | 0.0052 | 23.7333 | 76.2667 | 12 | 1.0000 |
| `limited` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0287 | 0.3593 | 0.1180 | 0.1464 | 1.9160 | 0.0000 | 0.0000 | 0.1947 | 0.0184 | 19 | 0.0044 | 20.2667 | 79.4667 | 13 | 1.0000 |
| `limited` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0338 | 0.4219 | 0.1163 | 0.1531 | 1.9148 | 0.0000 | 0.0000 | 0.1923 | 0.0184 | 18 | 0.0093 | 25.8667 | 74.1333 | 13 | 0.9231 |
| `limited` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0301 | 0.3758 | 0.1182 | 0.1565 | 1.9115 | 0.0000 | 0.0000 | 0.1939 | 0.0124 | 12 | 0.0109 | 22.1333 | 77.8667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3792 | 0.0303 | 0.1210 | 0.1526 | 0.0000 | 0.0000 | 0.0139 | 14.0000 | 0.0119 | 22.7833 | 77.1667 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
