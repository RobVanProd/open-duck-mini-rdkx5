# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `best_walk` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0367 | 0.4591 | 0.1040 | 0.1520 | 5.0040 | 2.2540 | 0.2637 |
| `best_walk` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0400 | 0.4997 | 0.1008 | 0.1554 | 5.1842 | 2.4342 | 0.2642 |
| `best_walk` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0388 | 0.4852 | 0.1038 | 0.1511 | 5.0962 | 2.3462 | 0.2606 |
| `best_walk` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 64 | `fall_or_nan` | -0.3375 | -4.2187 | 0.2059 | 0.0308 | 5.2400 | 2.9541 | 0.2940 |
| `best_walk` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0409 | 0.5117 | 0.1052 | 0.1505 | 5.1465 | 2.3965 | 0.2598 |
| `best_walk` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0388 | 0.4851 | 0.1005 | 0.1452 | 5.2297 | 2.4797 | 0.2651 |
| `best_walk` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0388 | 0.4854 | 0.1026 | 0.1552 | 5.0401 | 2.2901 | 0.2590 |
| `best_walk` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0393 | 0.4911 | 0.1060 | 0.1556 | 4.9770 | 2.2270 | 0.2620 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `best_walk` | 8 | 1 | 7 | 664.2500 | 64 | 750 | -0.1002 | -0.0080 | 0.1161 | 0.1370 | 2.4227 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
