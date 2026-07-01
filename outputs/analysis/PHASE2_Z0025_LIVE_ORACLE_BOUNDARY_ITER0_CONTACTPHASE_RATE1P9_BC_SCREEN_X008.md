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
seeds: `[0, 3, 4, 6]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
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
| `rate1p9` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0289 | 0.3616 | 0.1180 | 0.1519 | 1.9118 | 0.0000 | 0.0000 | 0.1945 | 0.0120 | 14 | 0.0139 | 21.8667 | 78.1333 | 0 | NA |
| `rate1p9` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0255 | 0.3184 | 0.1177 | 0.1547 | 1.9116 | 0.0000 | 0.0000 | 0.1945 | 0.0121 | 9 | 0.0186 | 18.5333 | 81.4667 | 0 | NA |
| `rate1p9` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0318 | 0.3971 | 0.1120 | 0.1506 | 1.9211 | 0.0000 | 0.0000 | 0.1923 | 0.0117 | 12 | 0.0068 | 21.3333 | 78.6667 | 0 | NA |
| `rate1p9` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0312 | 0.3903 | 0.1130 | 0.1531 | 1.9065 | 0.0000 | 0.0000 | 0.1917 | 0.0181 | 17 | 0.0050 | 24.2667 | 75.7333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rate1p9` | 4 | 0 | 4 | 750.0000 | 750 | 750 | 0.3668 | 0.0293 | 0.1152 | 0.1526 | 0.0000 | 0.0000 | 0.0134 | 13.0000 | 0.0110 | 21.5000 | 78.5000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
