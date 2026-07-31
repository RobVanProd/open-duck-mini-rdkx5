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
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0024`
min_swing_segments_per_foot: `0`
min_swing_rel_x_range_p95_m: `0.0`
min_swing_peak_lift_m: `0.0`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0244 | 0.1519 | 0.3711 | 0.0000 | 0.0655 | 0.0015 | 0 | 0.0000 | 0.4000 | 99.6000 | 12 | 0.9167 |
| `gain099` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0003 | NA | 0.0375 | 0.1563 | 0.3171 | 0.0000 | 0.0644 | 0.0047 | 1 | 0.0073 | 1.3333 | 98.5333 | 13 | 1.0000 |
| `gain099` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0318 | 0.1511 | 0.3782 | 0.0000 | 0.0657 | 0.0082 | 1 | 0.0052 | 0.8000 | 99.2000 | 13 | 0.9231 |
| `gain099` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0020 | NA | 0.0261 | 0.1556 | 0.3963 | 0.0000 | 0.0631 | 0.0051 | 0 | 0.0000 | 0.1333 | 99.8667 | 13 | 1.0000 |
| `gain099` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0016 | NA | 0.0136 | 0.1506 | 0.3736 | 0.0000 | 0.0647 | 0.0022 | 0 | 0.0000 | 0.2667 | 99.7333 | 12 | 1.0000 |
| `gain099` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0036 | NA | 0.0255 | 0.1462 | 0.3865 | 0.0000 | 0.0688 | 0.0196 | 1 | 0.0037 | 0.4000 | 99.3333 | 13 | 1.0000 |
| `gain099` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0006 | NA | 0.0220 | 0.1531 | 0.2913 | 0.0000 | 0.0600 | 0.0178 | 1 | 0.0081 | 1.6000 | 98.4000 | 13 | 0.9231 |
| `gain099` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0002 | NA | 0.0283 | 0.1565 | 0.4027 | 0.0000 | 0.0654 | 0.0017 | 1 | 0.0009 | 0.9333 | 99.0667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0006 | 0.0262 | 0.1526 | 0.0000 | 0.0076 | 0.6250 | 0.0031 | 0.7333 | 99.2167 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
