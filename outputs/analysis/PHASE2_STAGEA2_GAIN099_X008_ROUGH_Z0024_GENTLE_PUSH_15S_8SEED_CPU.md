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
terrain_hfield_z_scale: `0.0024`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0316 | 0.3947 | 0.1108 | 0.1519 | 2.4084 | 0.0000 | 0.1919 | 0.0118 | 16 | 0.0128 | 23.7333 | 76.2667 | 12 | 0.9167 |
| `gain099` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0339 | 0.4235 | 0.1281 | 0.1563 | 2.3731 | 0.0000 | 0.1964 | 0.0129 | 18 | 0.0144 | 25.7333 | 74.1333 | 13 | 1.0000 |
| `gain099` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0345 | 0.4313 | 0.1067 | 0.1512 | 2.3795 | 0.0000 | 0.1938 | 0.0120 | 14 | 0.0125 | 25.8667 | 74.1333 | 13 | 0.9231 |
| `gain099` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0301 | 0.3766 | 0.1234 | 0.1552 | 2.3780 | 0.0000 | 0.1943 | 0.0130 | 17 | 0.0199 | 24.9333 | 75.0667 | 13 | 1.0000 |
| `gain099` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0380 | 0.4750 | 0.1111 | 0.1506 | 2.3457 | 0.0000 | 0.1913 | 0.0121 | 19 | 0.0070 | 28.2667 | 71.7333 | 12 | 1.0000 |
| `gain099` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0302 | 0.3781 | 0.1181 | 0.1464 | 2.3938 | 0.0000 | 0.1948 | 0.0185 | 19 | 0.0091 | 22.8000 | 76.9333 | 13 | 1.0000 |
| `gain099` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0343 | 0.4289 | 0.1125 | 0.1532 | 2.3882 | 0.0000 | 0.1937 | 0.0173 | 20 | 0.0090 | 26.5333 | 73.4667 | 13 | 0.9231 |
| `gain099` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3822 | 0.1054 | 0.1565 | 2.3751 | 0.0000 | 0.1954 | 0.0115 | 16 | 0.0120 | 24.0000 | 76.0000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4113 | 0.0329 | 0.1145 | 0.1527 | 0.0000 | 0.0136 | 17.3750 | 0.0121 | 25.2333 | 74.7167 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
