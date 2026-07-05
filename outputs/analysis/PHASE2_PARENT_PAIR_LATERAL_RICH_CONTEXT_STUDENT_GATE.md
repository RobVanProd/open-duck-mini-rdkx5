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
| `lateral_routed_student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0244 | 0.3049 | 0.1823 | 0.1591 | 1.5762 | 0.0000 | 0.0000 | 0.1913 | 0.0180 | 7 | 0.0211 | 21.0667 | 78.9333 | 12 | 0.9167 |
| `lateral_routed_student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0297 | 0.3710 | 0.1829 | 0.1577 | 1.5756 | 0.0000 | 0.0000 | 0.1884 | 0.0170 | 13 | 0.0271 | 23.3333 | 76.6667 | 13 | 1.0000 |
| `lateral_routed_student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3824 | 0.1795 | 0.1589 | 1.5858 | 0.0000 | 0.0000 | 0.1884 | 0.0174 | 22 | 0.0272 | 30.4000 | 69.6000 | 13 | 0.9231 |
| `lateral_routed_student` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0296 | 0.3706 | 0.1915 | 0.1573 | 1.5733 | 0.0000 | 0.0000 | 0.1872 | 0.0127 | 9 | 0.0256 | 25.2000 | 74.8000 | 13 | 0.9231 |
| `lateral_routed_student` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 493 | `fall_or_nan` | 0.0641 | 0.8013 | 0.3451 | 0.0032 | 1.5823 | 0.0000 | 0.0000 | 0.1843 | 0.0602 | 14 | 0.0139 | 25.1521 | 74.6450 | 6 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lateral_routed_student` | 5 | 1 | 4 | 698.6000 | 493 | 750 | 0.4460 | 0.0357 | 0.2163 | 0.1273 | 0.0000 | 0.0000 | 0.0251 | 13.0000 | 0.0230 | 25.0304 | 74.9290 | 11.4000 | 0.9526 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
