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
| `live_oracle_iter1_selective` | 0 | `HOLD_CANDIDATE_TERRAIN_SWING` | 250 | `duration_complete` | 0.0339 | 0.4238 | 0.0994 | 0.1519 | 2.3534 | 0.0000 | 0.1996 | 0.0119 | 6 | 0.0030 | 22.8000 | 77.2000 | 0 | NA |
| `live_oracle_iter1_selective` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0298 | 0.3719 | 0.1151 | 0.1563 | 2.4146 | 0.0000 | 0.1991 | 0.0131 | 5 | 0.0158 | 26.0000 | 73.6000 | 0 | NA |
| `live_oracle_iter1_selective` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0326 | 0.4077 | 0.1022 | 0.1511 | 2.4321 | 0.0000 | 0.1951 | 0.0106 | 8 | 0.0066 | 23.6000 | 76.4000 | 0 | NA |
| `live_oracle_iter1_selective` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 250 | `duration_complete` | 0.0274 | 0.3427 | 0.1235 | 0.1554 | 2.4649 | 0.0336 | 0.1911 | 0.0112 | 8 | 0.0034 | 28.4000 | 71.6000 | 0 | NA |
| `live_oracle_iter1_selective` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0347 | 0.4332 | 0.0954 | 0.1506 | 2.3668 | 0.0000 | 0.2001 | 0.0106 | 4 | 0.0054 | 20.4000 | 79.6000 | 0 | NA |
| `live_oracle_iter1_selective` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 53 | `fall_or_nan` | -0.2703 | -3.3791 | 0.0472 | 0.0732 | 5.0016 | 2.2516 | 0.2821 | 0.0345 | 2 | 0.0139 | 15.0943 | 79.2453 | 0 | NA |
| `live_oracle_iter1_selective` | 6 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0319 | 0.3986 | 0.0973 | 0.1531 | 2.4442 | 0.0000 | 0.2030 | 0.0180 | 4 | 0.0082 | 22.8000 | 77.2000 | 0 | NA |
| `live_oracle_iter1_selective` | 7 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0311 | 0.3885 | 0.1029 | 0.1565 | 2.3804 | 0.0000 | 0.2032 | 0.0107 | 1 | 0.0168 | 21.6000 | 78.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_iter1_selective` | 8 | 1 | 7 | 225.3750 | 53 | 250 | -0.0766 | -0.0061 | 0.0979 | 0.1435 | 0.2857 | 0.0151 | 4.7500 | 0.0091 | 22.5868 | 76.6557 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
