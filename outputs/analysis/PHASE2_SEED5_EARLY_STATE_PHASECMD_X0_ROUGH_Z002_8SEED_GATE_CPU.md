# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_early` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0006 | NA | 0.0051 | 0.1520 | 0.0549 | 0.0000 | 0.0313 | 0.0212 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |
| `seed5_early` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0030 | NA | 0.0533 | 0.1563 | 0.1159 | 0.0000 | 0.0362 | 0.0041 | 0 | 0.0000 | 2.0000 | 97.6000 | 0 | NA |
| `seed5_early` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0013 | NA | 0.0196 | 0.1512 | 0.1018 | 0.0000 | 0.0392 | 0.0079 | 1 | 0.0042 | 2.0000 | 98.0000 | 0 | NA |
| `seed5_early` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0086 | NA | 0.0546 | 0.1550 | 0.0626 | 0.0000 | 0.0492 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `seed5_early` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0033 | NA | 0.0032 | 0.1507 | 0.0574 | 0.0000 | 0.0335 | 0.0028 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |
| `seed5_early` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 44 | `fall_or_nan` | -0.3677 | NA | 0.0585 | 0.0386 | 1.0477 | 0.0000 | 0.2180 | 0.0305 | 2 | 0.0045 | 6.8182 | 84.0909 | 0 | NA |
| `seed5_early` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0010 | NA | 0.0083 | 0.1531 | 0.1718 | 0.0000 | 0.0364 | 0.0236 | 1 | 0.0159 | 5.6000 | 94.4000 | 0 | NA |
| `seed5_early` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0025 | NA | 0.0209 | 0.1565 | 0.2070 | 0.0000 | 0.0452 | 0.0163 | 0 | 0.0000 | 2.8000 | 97.2000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_early` | 8 | 1 | 7 | 224.2500 | 44 | 250 | NA | -0.0474 | 0.0279 | 0.1392 | 0.0000 | 0.0152 | 0.5000 | 0.0031 | 2.6023 | 96.2114 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
