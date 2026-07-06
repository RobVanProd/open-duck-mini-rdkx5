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
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0240 | 0.2994 | 0.1795 | 0.1574 | 1.5728 | 0.0000 | 0.0000 | 0.1874 | 0.0167 | 10 | 0.0259 | 20.5333 | 79.4667 | 12 | 0.9167 |
| `student` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0238 | 0.2978 | 0.1812 | 0.1574 | 1.5520 | 0.0000 | 0.0000 | 0.1878 | 0.0163 | 12 | 0.0149 | 21.8667 | 78.1333 | 13 | 1.0000 |
| `student` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0225 | 0.2806 | 0.1885 | 0.1590 | 1.5565 | 0.0000 | 0.0000 | 0.1901 | 0.0173 | 10 | 0.0172 | 19.6000 | 80.4000 | 13 | 0.9231 |
| `student` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0238 | 0.2969 | 0.1815 | 0.1582 | 1.5791 | 0.0000 | 0.0000 | 0.1866 | 0.0153 | 12 | 0.0223 | 21.2000 | 78.8000 | 13 | 1.0000 |
| `student` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0245 | 0.3065 | 0.1827 | 0.1584 | 1.5646 | 0.0000 | 0.0000 | 0.1884 | 0.0114 | 10 | 0.0203 | 20.6667 | 79.3333 | 12 | 1.0000 |
| `student` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 154 | `fall_or_nan` | 0.1363 | 1.7031 | 0.8275 | 0.0019 | 1.5513 | 0.0000 | 0.0000 | 0.1996 | 0.0596 | 2 | 0.0055 | 11.6883 | 87.6623 | 2 | 1.0000 |
| `student` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 682 | `fall_or_nan` | 0.0466 | 0.5823 | 0.2482 | -0.0039 | 1.5629 | 0.0000 | 0.0000 | 0.1856 | 0.0579 | 13 | 0.0143 | 19.6481 | 80.2053 | 12 | 0.9167 |
| `student` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0255 | 0.3182 | 0.1868 | 0.1590 | 1.5566 | 0.0000 | 0.0000 | 0.1896 | 0.0178 | 15 | 0.0204 | 22.8000 | 77.2000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `student` | 8 | 2 | 6 | 667.0000 | 154 | 750 | 0.5106 | 0.0408 | 0.2720 | 0.1184 | 0.0000 | 0.0000 | 0.0265 | 10.5000 | 0.0176 | 19.7504 | 80.1501 | 10.8750 | 0.9696 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
