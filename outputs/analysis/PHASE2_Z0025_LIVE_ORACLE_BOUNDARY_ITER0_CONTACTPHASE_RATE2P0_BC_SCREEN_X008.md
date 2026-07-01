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
| `rate2p0` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0242 | 0.3020 | 0.1116 | 0.1520 | 1.9413 | 0.0000 | 0.0000 | 0.1919 | 0.0124 | 14 | 0.0031 | 16.5333 | 83.4667 | 0 | NA |
| `rate2p0` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0214 | 0.2680 | 0.1157 | 0.1545 | 1.9468 | 0.0000 | 0.0143 | 0.1895 | 0.0120 | 9 | 0.0069 | 15.8667 | 84.1333 | 0 | NA |
| `rate2p0` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0256 | 0.3206 | 0.1043 | 0.1506 | 1.9395 | 0.0000 | 0.0374 | 0.1919 | 0.0116 | 9 | 0.0049 | 16.6667 | 83.3333 | 0 | NA |
| `rate2p0` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0260 | 0.3252 | 0.1062 | 0.1531 | 1.9267 | 0.0000 | 0.0501 | 0.1931 | 0.0185 | 17 | 0.0041 | 20.2667 | 79.7333 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rate2p0` | 4 | 0 | 4 | 750.0000 | 750 | 750 | 0.3040 | 0.0243 | 0.1095 | 0.1526 | 0.0000 | 0.0254 | 0.0136 | 12.2500 | 0.0048 | 17.3333 | 82.6667 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
