# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[1, 7]`
trace_seeds: `[1, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `baseline` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0335 | 0.4189 | 0.1165 | 0.1556 | 2.1074 | 0.1966 |
| `baseline` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0374 | 0.4674 | 0.1177 | 0.1559 | 2.0841 | 0.1955 |
| `behavior_smoke` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | -0.0014 | -0.0179 | 0.0124 | 0.1556 | 0.5553 | 0.0631 |
| `behavior_smoke` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0001 | 0.0006 | 0.0140 | 0.1559 | 0.7172 | 0.0616 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 2 | 0 | 2 | 750.0000 | 750 | 750 | 0.4432 | 0.0355 | 0.1171 | 0.1557 |
| `behavior_smoke` | 2 | 0 | 2 | 750.0000 | 750 | 750 | -0.0086 | -0.0007 | 0.0132 | 0.1557 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
