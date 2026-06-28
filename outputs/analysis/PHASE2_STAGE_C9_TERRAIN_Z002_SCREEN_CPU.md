# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[2, 4]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c9_0` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0286 | 0.3577 | 0.1057 | 0.1511 | 1.5021 | 0.0000 | 0.1815 | 0.0096 | 3 | 0.0059 | 18.8000 | 81.2000 | 0 | NA |
| `c9_0` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0153 | 0.1918 | 0.0761 | 0.1506 | 1.5353 | 0.0000 | 0.1739 | 0.0015 | 0 | 0.0000 | 4.0000 | 96.0000 | 0 | NA |
| `c9_27360` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0137 | 0.1713 | 0.0883 | 0.1510 | 1.5121 | 0.0000 | 0.1888 | 0.0087 | 1 | 0.0045 | 7.6000 | 92.4000 | 0 | NA |
| `c9_27360` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0081 | 0.1012 | 0.0164 | 0.1506 | 1.4260 | 0.0000 | 0.1526 | 0.0018 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |
| `c9_54720` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0090 | 0.1125 | 0.0703 | 0.1511 | 1.2596 | 0.0000 | 0.1591 | 0.0068 | 1 | 0.0064 | 5.6000 | 94.4000 | 0 | NA |
| `c9_54720` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0059 | 0.0735 | 0.0085 | 0.1506 | 1.2456 | 0.0000 | 0.1419 | 0.0018 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |
| `c9_82080` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0157 | 0.1959 | 0.0903 | 0.1511 | 1.3248 | 0.0000 | 0.1640 | 0.0070 | 1 | 0.0064 | 10.0000 | 90.0000 | 0 | NA |
| `c9_82080` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0077 | 0.0964 | 0.0242 | 0.1506 | 1.3055 | 0.0000 | 0.1438 | 0.0018 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c9_0` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.2748 | 0.0220 | 0.0909 | 0.1509 | 0.0000 | 0.0055 | 1.5000 | 0.0029 | 11.4000 | 88.6000 | 0.0000 | NA |
| `c9_27360` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.1363 | 0.0109 | 0.0523 | 0.1508 | 0.0000 | 0.0053 | 0.5000 | 0.0023 | 4.2000 | 95.8000 | 0.0000 | NA |
| `c9_54720` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.0930 | 0.0074 | 0.0394 | 0.1508 | 0.0000 | 0.0043 | 0.5000 | 0.0032 | 3.2000 | 96.8000 | 0.0000 | NA |
| `c9_82080` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.1461 | 0.0117 | 0.0573 | 0.1509 | 0.0000 | 0.0044 | 0.5000 | 0.0032 | 5.4000 | 94.6000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
