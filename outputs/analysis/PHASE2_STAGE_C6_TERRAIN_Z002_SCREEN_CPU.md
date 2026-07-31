# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c6_0` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0325 | 0.4061 | 0.1399 | 0.1519 | 1.7902 | 0.0000 | 0.2046 | 0.0165 | 20.8000 | 79.2000 | 0 | NA |
| `c6_81920` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0079 | 0.0985 | 0.0721 | 0.1519 | 1.4702 | 0.0000 | 0.1654 | 0.0072 | 4.0000 | 96.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c6_0` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.4061 | 0.0325 | 0.1399 | 0.1519 | 0.0000 | 0.0165 | 20.8000 | 79.2000 | 0.0000 | NA |
| `c6_81920` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.0985 | 0.0079 | 0.0721 | 0.1519 | 0.0000 | 0.0072 | 4.0000 | 96.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
