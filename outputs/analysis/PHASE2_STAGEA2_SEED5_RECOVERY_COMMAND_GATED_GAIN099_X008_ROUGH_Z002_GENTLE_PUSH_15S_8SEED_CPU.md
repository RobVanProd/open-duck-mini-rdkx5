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
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0319 | 0.3991 | 0.1118 | 0.1519 | 2.3672 | 0.0000 | 0.1934 | 0.0120 | 15 | 0.0195 | 24.2667 | 75.7333 | 12 | 0.9167 |
| `gain099` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0349 | 0.4362 | 0.1189 | 0.1563 | 2.3530 | 0.0000 | 0.1912 | 0.0123 | 19 | 0.0151 | 27.6000 | 72.2667 | 13 | 1.0000 |
| `gain099` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0349 | 0.4359 | 0.1089 | 0.1511 | 2.3372 | 0.0000 | 0.1920 | 0.0126 | 14 | 0.0191 | 26.8000 | 73.2000 | 13 | 0.9231 |
| `gain099` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3828 | 0.1212 | 0.1548 | 2.3950 | 0.0000 | 0.1904 | 0.0129 | 17 | 0.0141 | 25.4667 | 74.5333 | 13 | 1.0000 |
| `gain099` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0360 | 0.4494 | 0.1070 | 0.1507 | 2.3560 | 0.0000 | 0.1905 | 0.0116 | 21 | 0.0063 | 27.0667 | 72.9333 | 12 | 1.0000 |
| `gain099` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0299 | 0.3736 | 0.1169 | 0.1464 | 2.3911 | 0.0000 | 0.1944 | 0.0186 | 16 | 0.0083 | 22.1333 | 77.6000 | 13 | 1.0000 |
| `gain099` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0334 | 0.4181 | 0.1128 | 0.1531 | 2.3559 | 0.0000 | 0.1934 | 0.0169 | 20 | 0.0092 | 26.1333 | 73.8667 | 13 | 0.9231 |
| `gain099` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0311 | 0.3883 | 0.1048 | 0.1565 | 2.3693 | 0.0000 | 0.1938 | 0.0117 | 16 | 0.0134 | 25.2000 | 74.8000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4104 | 0.0328 | 0.1128 | 0.1526 | 0.0000 | 0.0136 | 17.2500 | 0.0131 | 25.5833 | 74.3667 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
