# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[1, 4]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `blend001` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0371 | 0.4634 | 0.1003 | 0.1556 | 3.6430 | 0.2516 |
| `blend001` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0405 | 0.5060 | 0.1023 | 0.1506 | 3.6885 | 0.2575 |
| `blend002` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0371 | 0.4635 | 0.0992 | 0.1556 | 3.6789 | 0.2547 |
| `blend002` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0424 | 0.5298 | 0.0994 | 0.1506 | 3.6811 | 0.2544 |
| `blend005` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0378 | 0.4722 | 0.1002 | 0.1556 | 3.7071 | 0.2554 |
| `blend005` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0412 | 0.5155 | 0.1024 | 0.1506 | 3.7168 | 0.2600 |
| `blend010` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0369 | 0.4609 | 0.1008 | 0.1556 | 3.7442 | 0.2522 |
| `blend010` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0433 | 0.5410 | 0.1058 | 0.1506 | 3.7533 | 0.2556 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `blend001` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4847 | 0.0388 | 0.1013 | 0.1531 |
| `blend002` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4966 | 0.0397 | 0.0993 | 0.1531 |
| `blend005` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4939 | 0.0395 | 0.1013 | 0.1531 |
| `blend010` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.5010 | 0.0401 | 0.1033 | 0.1531 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
