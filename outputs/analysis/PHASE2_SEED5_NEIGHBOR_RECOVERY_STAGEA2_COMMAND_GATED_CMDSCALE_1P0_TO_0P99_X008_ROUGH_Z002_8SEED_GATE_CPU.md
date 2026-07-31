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
| `scaled` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0333 | 0.4159 | 0.1015 | 0.1519 | 2.4127 | 0.0000 | 0.1920 | 0.0115 | 3 | 0.0054 | 20.8000 | 79.2000 | 0 | NA |
| `scaled` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0326 | 0.4072 | 0.1172 | 0.1563 | 2.2773 | 0.0000 | 0.1937 | 0.0118 | 5 | 0.0184 | 26.8000 | 72.8000 | 0 | NA |
| `scaled` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0384 | 0.4805 | 0.0983 | 0.1511 | 2.3163 | 0.0000 | 0.1927 | 0.0111 | 4 | 0.0076 | 24.8000 | 75.2000 | 0 | NA |
| `scaled` | 3 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0243 | 0.3038 | 0.1124 | 0.1548 | 2.4004 | 0.0000 | 0.1860 | 0.0105 | 5 | 0.0025 | 20.0000 | 80.0000 | 0 | NA |
| `scaled` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0332 | 0.4154 | 0.1035 | 0.1507 | 2.4287 | 0.0000 | 0.1970 | 0.0109 | 3 | 0.0037 | 20.4000 | 79.6000 | 0 | NA |
| `scaled` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0379 | 0.4738 | 0.1213 | 0.1464 | 2.3250 | 0.0000 | 0.1979 | 0.0184 | 5 | 0.0081 | 20.4000 | 78.8000 | 0 | NA |
| `scaled` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0326 | 0.4072 | 0.1029 | 0.1531 | 2.3529 | 0.0000 | 0.1945 | 0.0171 | 5 | 0.0085 | 24.8000 | 75.2000 | 0 | NA |
| `scaled` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0256 | 0.3198 | 0.0938 | 0.1565 | 2.3860 | 0.0000 | 0.1987 | 0.0114 | 5 | 0.0049 | 21.2000 | 78.8000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `scaled` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4030 | 0.0322 | 0.1064 | 0.1526 | 0.0000 | 0.0128 | 4.3750 | 0.0074 | 22.4000 | 77.4500 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
