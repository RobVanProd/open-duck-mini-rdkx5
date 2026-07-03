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
| `detached_40960` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0041 | 0.0507 | 0.1004 | 0.1522 | 1.8848 | 0.0000 | 1.5458 | 0.1676 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `detached_81920` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 87 | `fall_or_nan` | 0.2235 | 2.7935 | 1.1602 | 0.0035 | 5.2400 | 2.9900 | 3.2400 | 0.2336 | 0.0568 | 1 | 0.0094 | 4.5977 | 91.9540 | 0 | NA |
| `detached_122880` | 0 | `HOLD_CANDIDATE_ACTION_SATURATION` | 250 | `duration_complete` | 0.0393 | 0.4915 | 0.3686 | 0.1367 | 5.2400 | 2.9900 | 3.2400 | 0.2269 | -0.0001 | 0 | 0.0000 | 6.0000 | 94.0000 | 0 | NA |
| `exec_40960` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0036 | 0.0455 | 0.1209 | 0.1522 | 2.0724 | 0.0000 | 2.2993 | 0.1753 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 0 | NA |
| `exec_81920` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 87 | `fall_or_nan` | 0.2256 | 2.8200 | 1.1720 | -0.0005 | 5.2400 | 2.9900 | 3.2400 | 0.2314 | 0.0572 | 2 | 0.0078 | 5.7471 | 90.8046 | 0 | NA |
| `exec_122880` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0110 | 0.1373 | 0.1373 | 0.1522 | 3.3742 | 1.1242 | 2.9900 | 0.1970 | 0.0001 | 0 | 0.0000 | 3.6000 | 96.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `detached_40960` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.0507 | 0.0041 | 0.1004 | 0.1522 | 0.0000 | 1.5458 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `detached_81920` | 1 | 1 | 0 | 87.0000 | 87 | 87 | 2.7935 | 0.2235 | 1.1602 | 0.0035 | 2.9900 | 3.2400 | 0.0568 | 1.0000 | 0.0094 | 4.5977 | 91.9540 | 0.0000 | NA |
| `detached_122880` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.4915 | 0.0393 | 0.3686 | 0.1367 | 2.9900 | 3.2400 | -0.0001 | 0.0000 | 0.0000 | 6.0000 | 94.0000 | 0.0000 | NA |
| `exec_40960` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.0455 | 0.0036 | 0.1209 | 0.1522 | 0.0000 | 2.2993 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 0.0000 | NA |
| `exec_81920` | 1 | 1 | 0 | 87.0000 | 87 | 87 | 2.8200 | 0.2256 | 1.1720 | -0.0005 | 2.9900 | 3.2400 | 0.0572 | 2.0000 | 0.0078 | 5.7471 | 90.8046 | 0.0000 | NA |
| `exec_122880` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.1373 | 0.0110 | 0.1373 | 0.1522 | 1.1242 | 2.9900 | 0.0001 | 0.0000 | 0.0000 | 3.6000 | 96.4000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
