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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0114 | 0.1427 | 0.0880 | 0.1520 | 1.5504 | 0.0000 | 0.1686 |
| `stage_a` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0083 | 0.1038 | 0.0900 | 0.1556 | 1.5397 | 0.0000 | 0.1634 |
| `stage_a` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0128 | 0.1603 | 0.0937 | 0.1509 | 1.5513 | 0.0000 | 0.1712 |
| `stage_a` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0083 | 0.1041 | 0.0949 | 0.1547 | 1.5466 | 0.0000 | 0.1657 |
| `stage_a` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0023 | 0.0284 | 0.0338 | 0.1506 | 0.4294 | 0.0000 | 0.0754 |
| `stage_a` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0132 | 0.1654 | 0.0922 | 0.1463 | 1.5264 | 0.0000 | 0.1700 |
| `stage_a` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | -0.0009 | -0.0111 | 0.0334 | 0.1557 | 0.4479 | 0.0000 | 0.0756 |
| `stage_a` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0075 | 0.0931 | 0.0931 | 0.1559 | 1.5313 | 0.0000 | 0.1663 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.0984 | 0.0079 | 0.0774 | 0.1527 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
