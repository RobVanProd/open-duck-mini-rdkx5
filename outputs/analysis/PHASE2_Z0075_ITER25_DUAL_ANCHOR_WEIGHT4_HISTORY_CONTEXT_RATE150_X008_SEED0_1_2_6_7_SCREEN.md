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
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter25` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 525 | `fall_or_nan` | 0.0578 | 0.7229 | 0.3231 | 0.0048 | 1.5498 | 0.0000 | 0.0000 | 0.1831 | 0.0630 | 8 | 0.0123 | 22.0952 | 77.5238 | 8 | 0.8750 |
| `iter25` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3567 | 0.1739 | 0.1579 | 1.5635 | 0.0000 | 0.0000 | 0.1892 | 0.0142 | 14 | 0.0215 | 24.5333 | 75.4667 | 13 | 0.9231 |
| `iter25` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0305 | 0.3816 | 0.1878 | 0.1567 | 1.5450 | 0.0000 | 0.0000 | 0.1836 | 0.0179 | 14 | 0.0251 | 27.4667 | 72.5333 | 13 | 0.9231 |
| `iter25` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3273 | 0.1904 | 0.1580 | 1.5479 | 0.0000 | 0.0000 | 0.1881 | 0.0121 | 11 | 0.0255 | 23.8667 | 76.1333 | 13 | 0.9231 |
| `iter25` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 470 | `fall_or_nan` | 0.0666 | 0.8327 | 0.3586 | 0.0108 | 1.5580 | 0.0000 | 0.0000 | 0.1875 | 0.0612 | 9 | 0.0198 | 25.9574 | 73.8298 | 6 | 0.8333 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter25` | 5 | 2 | 3 | 649.0000 | 470 | 750 | 0.5242 | 0.0419 | 0.2467 | 0.0976 | 0.0000 | 0.0000 | 0.0337 | 11.2000 | 0.0209 | 24.7839 | 75.0974 | 10.6000 | 0.8955 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
