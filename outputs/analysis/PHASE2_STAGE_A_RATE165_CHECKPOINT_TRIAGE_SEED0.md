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
seeds: `[0]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0026`
reset_settle_ticks: `0`
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
| `s655360` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0005 | 0.0065 | 0.0124 | 0.1523 | 0.2372 | 0.0000 | 0.0000 | 0.0506 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `s1310720` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0005 | 0.0066 | 0.0103 | 0.1523 | 0.1563 | 0.0000 | 0.0000 | 0.0444 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `s1966080` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0006 | 0.0076 | 0.0185 | 0.1523 | 0.1416 | 0.0000 | 0.0000 | 0.0446 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `s2621440` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0006 | 0.0081 | 0.0213 | 0.1523 | 0.1160 | 0.0000 | 0.0000 | 0.0446 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `s3276800` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0007 | 0.0085 | 0.0248 | 0.1523 | 0.1014 | 0.0000 | 0.0000 | 0.0416 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `s3932160` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0007 | 0.0089 | 0.0281 | 0.1523 | 0.0887 | 0.0000 | 0.0000 | 0.0395 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `s4587520` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0007 | 0.0091 | 0.0305 | 0.1523 | 0.0838 | 0.0000 | 0.0000 | 0.0385 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `s655360` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.0065 | 0.0005 | 0.0124 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `s1310720` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.0066 | 0.0005 | 0.0103 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `s1966080` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.0076 | 0.0006 | 0.0185 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `s2621440` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.0081 | 0.0006 | 0.0213 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `s3276800` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.0085 | 0.0007 | 0.0248 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `s3932160` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.0089 | 0.0007 | 0.0281 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `s4587520` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.0091 | 0.0007 | 0.0305 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
