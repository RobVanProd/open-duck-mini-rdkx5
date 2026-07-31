# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0295 | 0.3681 | 0.1543 | 0.1527 | 1.7764 | 0.0000 | 0.2008 | 0 | NA |
| `stage_a` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0296 | 0.3695 | 0.1577 | 0.1565 | 1.7968 | 0.0000 | 0.2009 | 0 | NA |
| `stage_a` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0272 | 0.3400 | 0.1415 | 0.1514 | 1.7928 | 0.0000 | 0.2015 | 0 | NA |
| `stage_a` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0258 | 0.3221 | 0.1372 | 0.1559 | 1.7724 | 0.0000 | 0.1938 | 0 | NA |
| `stage_a` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0287 | 0.3591 | 0.1563 | 0.1508 | 1.7924 | 0.0000 | 0.1991 | 0 | NA |
| `stage_a` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | `fall_or_nan` | -0.2280 | -2.8498 | 0.0836 | 0.0700 | 1.7123 | 0.0000 | 0.2083 | 0 | NA |
| `stage_a` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0277 | 0.3464 | 0.1491 | 0.1531 | 1.7548 | 0.0000 | 0.2019 | 0 | NA |
| `stage_a` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0285 | 0.3568 | 0.1503 | 0.1565 | 1.7814 | 0.0000 | 0.2007 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 8 | 1 | 7 | 664.3750 | 65 | 750 | -0.0485 | -0.0039 | 0.1413 | 0.1434 | 0.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
