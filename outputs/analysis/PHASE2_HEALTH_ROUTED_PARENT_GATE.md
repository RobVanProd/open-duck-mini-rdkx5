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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `routed_parent` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 677 | `fall_or_nan` | 0.0002 | 0.0027 | 0.1702 | 0.0608 | 1.5535 | 0.0000 | 0.0000 | 0.1777 | 0.0338 | 8 | 0.0200 | 24.3722 | 75.4801 | 11 | 0.9091 |
| `routed_parent` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0316 | 0.3945 | 0.1716 | 0.1590 | 1.5499 | 0.0000 | 0.0000 | 0.1833 | 0.0172 | 17 | 0.0234 | 25.4667 | 74.5333 | 13 | 1.0000 |
| `routed_parent` | 2 | `HOLD_CANDIDATE_BASE_HEIGHT` | 750 | `duration_complete` | 0.0448 | 0.5602 | 0.2119 | 0.1027 | 1.5575 | 0.0000 | 0.0000 | 0.1861 | 0.0371 | 20 | 0.0197 | 26.0000 | 74.0000 | 13 | 0.9231 |
| `routed_parent` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 478 | `fall_or_nan` | -0.0084 | -0.1046 | 0.2194 | 0.0790 | 1.5625 | 0.0000 | 0.0000 | 0.1853 | 0.0202 | 12 | 0.0220 | 25.9414 | 74.0586 | 8 | 0.8750 |
| `routed_parent` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 584 | `fall_or_nan` | 0.0618 | 0.7719 | 0.3283 | -0.0009 | 1.5578 | 0.0000 | 0.0000 | 0.1865 | 0.0597 | 14 | 0.0169 | 27.7397 | 72.0890 | 8 | 0.8750 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `routed_parent` | 5 | 3 | 2 | 647.8000 | 478 | 750 | 0.3249 | 0.0260 | 0.2203 | 0.0801 | 0.0000 | 0.0000 | 0.0336 | 14.2000 | 0.0204 | 25.9040 | 74.0322 | 10.6000 | 0.9164 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
