# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.1`-`0.2`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0025`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0001 | NA | 0.0409 | 0.1519 | 2.7472 | 0.0000 | 0.0000 | 0.1918 | 0.0006 | 0 | 0.0000 | 1.2000 | 98.8000 | 12 | 0.9167 |
| `limited` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0012 | NA | 0.0724 | 0.1563 | 2.8144 | 0.0000 | 0.0000 | 0.1903 | 0.0035 | 0 | 0.0000 | 1.3333 | 98.5333 | 13 | 1.0000 |
| `limited` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0005 | NA | 0.0412 | 0.1513 | 2.7746 | 0.0000 | 0.0000 | 0.1956 | 0.0063 | 1 | 0.0038 | 2.2667 | 97.7333 | 13 | 0.9231 |
| `limited` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0025 | NA | 0.0614 | 0.1556 | 2.7472 | 0.0000 | 0.0000 | 0.1955 | 0.0011 | 0 | 0.0000 | 1.6000 | 98.4000 | 13 | 1.0000 |
| `limited` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0003 | NA | 0.0260 | 0.1505 | 2.7590 | 0.0000 | 0.0000 | 0.1973 | 0.0072 | 1 | 0.0039 | 2.4000 | 97.6000 | 12 | 1.0000 |
| `limited` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0008 | NA | 0.0201 | 0.1457 | 2.7472 | 0.0000 | 0.0000 | 0.1953 | 0.0196 | 3 | 0.0089 | 3.7333 | 96.0000 | 13 | 1.0000 |
| `limited` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0006 | NA | 0.0384 | 0.1530 | 2.7472 | 0.0000 | 0.0000 | 0.1933 | 0.0164 | 1 | 0.0136 | 1.6000 | 98.4000 | 13 | 0.9231 |
| `limited` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0003 | NA | 0.0378 | 0.1565 | 2.7472 | 0.0000 | 0.0000 | 0.1932 | 0.0023 | 1 | 0.0015 | 2.2667 | 97.7333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | -0.0004 | 0.0423 | 0.1526 | 0.0000 | 0.0000 | 0.0071 | 0.8750 | 0.0040 | 2.0500 | 97.9000 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
