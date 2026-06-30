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
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
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
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0312 | 0.3894 | 0.1096 | 0.1519 | 2.3568 | 0.0000 | 0.1950 | 0.0116 | 15 | 0.0183 | 24.2667 | 75.7333 | 0 | NA |
| `gain099` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0352 | 0.4396 | 0.1164 | 0.1563 | 2.3436 | 0.0000 | 0.1916 | 0.0124 | 17 | 0.0105 | 27.3333 | 72.5333 | 0 | NA |
| `gain099` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0350 | 0.4377 | 0.1063 | 0.1512 | 2.3872 | 0.0000 | 0.1933 | 0.0123 | 14 | 0.0107 | 26.5333 | 73.4667 | 0 | NA |
| `gain099` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0288 | 0.3602 | 0.1121 | 0.1552 | 2.3585 | 0.0000 | 0.1915 | 0.0118 | 16 | 0.0204 | 23.3333 | 76.6667 | 0 | NA |
| `gain099` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0347 | 0.4337 | 0.1103 | 0.1506 | 2.3845 | 0.0000 | 0.1928 | 0.0118 | 18 | 0.0074 | 26.4000 | 73.6000 | 0 | NA |
| `gain099` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0303 | 0.3794 | 0.1127 | 0.1464 | 2.3999 | 0.0000 | 0.1953 | 0.0184 | 18 | 0.0088 | 22.6667 | 77.0667 | 0 | NA |
| `gain099` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0345 | 0.4317 | 0.1003 | 0.1532 | 2.3824 | 0.0000 | 0.1927 | 0.0172 | 18 | 0.0069 | 26.4000 | 73.6000 | 0 | NA |
| `gain099` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0291 | 0.3632 | 0.1051 | 0.1565 | 2.3808 | 0.0000 | 0.1934 | 0.0117 | 15 | 0.0107 | 24.5333 | 75.4667 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4044 | 0.0323 | 0.1091 | 0.1527 | 0.0000 | 0.0134 | 16.3750 | 0.0117 | 25.1833 | 74.7667 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
