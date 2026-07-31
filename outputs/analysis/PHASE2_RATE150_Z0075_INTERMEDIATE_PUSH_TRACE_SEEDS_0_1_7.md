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
seeds: `[0, 1, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[0, 1, 7]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 181 | `fall_or_nan` | 0.1271 | 1.5887 | 0.7706 | 0.0094 | 1.5939 | 0.0000 | 1.3268 | 0.2007 | 0.0169 | 2 | 0.0145 | 18.7845 | 81.2155 | 2 | 1.0000 |
| `phase_mod_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0309 | 0.3864 | 0.1878 | 0.1533 | 1.5960 | 0.0000 | 0.0000 | 0.1909 | 0.0156 | 15 | 0.0154 | 22.8000 | 77.2000 | 13 | 1.0000 |
| `phase_mod_rate150` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 550 | `fall_or_nan` | 0.0580 | 0.7245 | 0.3386 | 0.0201 | 1.5628 | 0.0000 | 0.4477 | 0.1872 | 0.0601 | 11 | 0.0225 | 23.4545 | 76.3636 | 7 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 3 | 2 | 1 | 493.6667 | 181 | 750 | 0.8999 | 0.0720 | 0.4324 | 0.0609 | 0.0000 | 0.5915 | 0.0309 | 9.3333 | 0.0175 | 21.6797 | 78.2597 | 7.3333 | 1.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
