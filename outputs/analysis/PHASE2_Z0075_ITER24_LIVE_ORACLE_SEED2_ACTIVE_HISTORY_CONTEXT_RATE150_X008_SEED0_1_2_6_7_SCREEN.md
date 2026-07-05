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
| `iter24` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0261 | 0.3256 | 0.1922 | 0.1591 | 1.5713 | 0.0000 | 0.0000 | 0.1836 | 0.0181 | 13 | 0.0285 | 23.6000 | 76.4000 | 12 | 0.9167 |
| `iter24` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0287 | 0.3584 | 0.1786 | 0.1585 | 1.5572 | 0.0000 | 0.0000 | 0.1854 | 0.0158 | 12 | 0.0230 | 23.8667 | 76.1333 | 13 | 0.9231 |
| `iter24` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3278 | 0.1822 | 0.1590 | 1.5779 | 0.0000 | 0.0000 | 0.1886 | 0.0169 | 13 | 0.0224 | 24.0000 | 76.0000 | 13 | 0.9231 |
| `iter24` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 250 | `fall_or_nan` | -0.0453 | -0.5659 | 0.2187 | 0.0690 | 1.5557 | 0.0000 | 0.0000 | 0.1794 | 0.0338 | 5 | 0.0251 | 23.2000 | 76.8000 | 4 | 0.7500 |
| `iter24` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0275 | 0.3437 | 0.1863 | 0.1565 | 1.5715 | 0.0000 | 0.0000 | 0.1876 | 0.0173 | 15 | 0.0208 | 24.5333 | 75.4667 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter24` | 5 | 1 | 4 | 650.0000 | 250 | 750 | 0.1579 | 0.0126 | 0.1916 | 0.1404 | 0.0000 | 0.0000 | 0.0204 | 11.6000 | 0.0239 | 23.8400 | 76.1600 | 10.4000 | 0.8826 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
