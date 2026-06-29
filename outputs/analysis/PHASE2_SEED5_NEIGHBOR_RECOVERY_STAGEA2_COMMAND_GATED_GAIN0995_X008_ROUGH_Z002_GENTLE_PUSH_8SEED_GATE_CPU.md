# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `0.995`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.05`-`0.1`
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
| `gated` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0318 | 0.3972 | 0.1002 | 0.1519 | 2.3949 | 0.0000 | 0.1930 | 0.0117 | 5 | 0.0052 | 21.2000 | 78.8000 | 4 | 0.7500 |
| `gated` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0318 | 0.3978 | 0.1321 | 0.1563 | 2.3582 | 0.0000 | 0.1965 | 0.0127 | 7 | 0.0171 | 26.0000 | 73.6000 | 4 | 1.0000 |
| `gated` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0394 | 0.4919 | 0.1123 | 0.1511 | 2.2520 | 0.0000 | 0.1908 | 0.0118 | 7 | 0.0103 | 29.6000 | 70.4000 | 4 | 0.7500 |
| `gated` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0247 | 0.3084 | 0.1244 | 0.1548 | 2.3414 | 0.0000 | 0.1894 | 0.0109 | 5 | 0.0046 | 22.4000 | 77.6000 | 4 | 1.0000 |
| `gated` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0367 | 0.4593 | 0.1054 | 0.1507 | 2.3421 | 0.0000 | 0.1956 | 0.0110 | 4 | 0.0112 | 23.2000 | 76.8000 | 4 | 0.7500 |
| `gated` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0357 | 0.4460 | 0.1149 | 0.1464 | 2.3232 | 0.0000 | 0.1951 | 0.0182 | 6 | 0.0080 | 17.6000 | 81.6000 | 4 | 1.0000 |
| `gated` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0355 | 0.4437 | 0.1247 | 0.1531 | 2.3672 | 0.0000 | 0.1919 | 0.0170 | 8 | 0.0077 | 28.8000 | 71.2000 | 4 | 1.0000 |
| `gated` | 7 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0300 | 0.3750 | 0.0952 | 0.1565 | 2.3726 | 0.0000 | 0.2005 | 0.0121 | 3 | 0.0107 | 22.4000 | 77.6000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.4149 | 0.0332 | 0.1136 | 0.1526 | 0.0000 | 0.0132 | 5.6250 | 0.0093 | 23.9000 | 75.9500 | 3.8750 | 0.9062 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
