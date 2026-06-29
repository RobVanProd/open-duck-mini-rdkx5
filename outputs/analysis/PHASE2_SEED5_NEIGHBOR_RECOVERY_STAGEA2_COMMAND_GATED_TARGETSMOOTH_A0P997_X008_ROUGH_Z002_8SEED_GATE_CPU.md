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
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
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
| `smooth` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0349 | 0.4358 | 0.1042 | 0.1519 | 2.3700 | 0.0000 | 0.1963 | 0.0117 | 4 | 0.0106 | 24.0000 | 76.0000 | 0 | NA |
| `smooth` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0342 | 0.4270 | 0.1255 | 0.1563 | 2.3675 | 0.0000 | 0.1936 | 0.0125 | 6 | 0.0179 | 28.4000 | 71.2000 | 0 | NA |
| `smooth` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0411 | 0.5140 | 0.0982 | 0.1511 | 2.4141 | 0.0000 | 0.1943 | 0.0116 | 7 | 0.0063 | 28.8000 | 71.2000 | 0 | NA |
| `smooth` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0255 | 0.3184 | 0.1118 | 0.1548 | 2.4146 | 0.0000 | 0.1922 | 0.0110 | 4 | 0.0036 | 20.8000 | 79.2000 | 0 | NA |
| `smooth` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0372 | 0.4645 | 0.1063 | 0.1507 | 2.3387 | 0.0000 | 0.1959 | 0.0107 | 4 | 0.0091 | 22.8000 | 77.2000 | 0 | NA |
| `smooth` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0354 | 0.4424 | 0.1121 | 0.1464 | 2.4109 | 0.0000 | 0.1991 | 0.0183 | 4 | 0.0078 | 18.0000 | 81.2000 | 0 | NA |
| `smooth` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0360 | 0.4495 | 0.1031 | 0.1531 | 2.3550 | 0.0000 | 0.1954 | 0.0170 | 6 | 0.0080 | 29.6000 | 70.4000 | 0 | NA |
| `smooth` | 7 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0268 | 0.3350 | 0.1053 | 0.1565 | 2.4117 | 0.0000 | 0.2013 | 0.0106 | 4 | 0.0149 | 20.8000 | 79.2000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `smooth` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4233 | 0.0339 | 0.1083 | 0.1526 | 0.0000 | 0.0129 | 4.8750 | 0.0098 | 24.1500 | 75.7000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
