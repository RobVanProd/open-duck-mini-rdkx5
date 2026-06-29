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
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `0`
min_swing_rel_x_range_p95_m: `0.0`
min_swing_peak_lift_m: `0.0`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0208 | 0.1519 | 0.3778 | 0.0000 | 0.0659 | 0.0017 | 0 | 0.0000 | 0.4000 | 99.6000 | 0 | NA |
| `gain099` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0003 | NA | 0.0316 | 0.1562 | 0.3220 | 0.0000 | 0.0644 | 0.0048 | 1 | 0.0016 | 1.2000 | 98.6667 | 0 | NA |
| `gain099` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0006 | NA | 0.0290 | 0.1511 | 0.3860 | 0.0000 | 0.0663 | 0.0077 | 1 | 0.0048 | 0.6667 | 99.3333 | 0 | NA |
| `gain099` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0020 | NA | 0.0166 | 0.1553 | 0.3997 | 0.0000 | 0.0656 | 0.0049 | 0 | 0.0000 | 0.1333 | 99.8667 | 0 | NA |
| `gain099` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0018 | NA | 0.0125 | 0.1506 | 0.3802 | 0.0000 | 0.0651 | 0.0024 | 0 | 0.0000 | 0.2667 | 99.7333 | 0 | NA |
| `gain099` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0037 | NA | 0.0189 | 0.1462 | 0.3706 | 0.0000 | 0.0656 | 0.0198 | 1 | 0.0037 | 0.4000 | 99.3333 | 0 | NA |
| `gain099` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0008 | NA | 0.0145 | 0.1530 | 0.3615 | 0.0000 | 0.0636 | 0.0176 | 1 | 0.0163 | 1.6000 | 98.4000 | 0 | NA |
| `gain099` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0002 | NA | 0.0240 | 0.1564 | 0.3872 | 0.0000 | 0.0641 | 0.0126 | 0 | 0.0000 | 0.6667 | 99.3333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0007 | 0.0210 | 0.1526 | 0.0000 | 0.0089 | 0.5000 | 0.0033 | 0.6667 | 99.2833 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
