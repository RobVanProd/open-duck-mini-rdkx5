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
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[0, 1, 2, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_contact` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 161 | `fall_or_nan` | 0.1343 | 1.6787 | 0.9100 | -0.0054 | 1.6523 | 0.0000 | 0.0000 | 0.1976 | 0.0615 | 2 | 0.0171 | 11.1801 | 85.7143 | 2 | 1.0000 |
| `phase_contact` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0288 | 0.3598 | 0.1804 | 0.1568 | 1.6535 | 0.0000 | 0.0000 | 0.1917 | 0.0129 | 10 | 0.0237 | 22.8000 | 77.2000 | 13 | 1.0000 |
| `phase_contact` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 158 | `fall_or_nan` | 0.1333 | 1.6668 | 0.8726 | 0.0054 | 1.6714 | 0.0000 | 0.0000 | 0.2003 | 0.0623 | 2 | 0.0132 | 13.9241 | 85.4430 | 2 | 1.0000 |
| `phase_contact` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 207 | `fall_or_nan` | 0.1128 | 1.4105 | 0.7205 | -0.0031 | 1.6137 | 0.0000 | 0.0000 | 0.1932 | 0.0599 | 3 | 0.0041 | 16.9082 | 82.1256 | 3 | 1.0000 |
| `phase_contact` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0280 | 0.3495 | 0.1660 | 0.1568 | 1.6489 | 0.0000 | 0.0000 | 0.1852 | 0.0125 | 13 | 0.0206 | 23.3333 | 76.6667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_contact` | 5 | 3 | 2 | 405.2000 | 158 | 750 | 1.0931 | 0.0874 | 0.5699 | 0.0621 | 0.0000 | 0.0000 | 0.0418 | 6.0000 | 0.0158 | 17.6291 | 81.4299 | 6.0000 | 1.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
