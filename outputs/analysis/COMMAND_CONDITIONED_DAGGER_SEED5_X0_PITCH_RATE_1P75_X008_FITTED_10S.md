# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0122 | 0.1527 | 0.1003 | 0.1520 | 1.6896 | 0.1749 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0083 | 0.1034 | 0.1104 | 0.1556 | 1.6266 | 0.1694 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0122 | 0.1523 | 0.1059 | 0.1509 | 1.6119 | 0.1736 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0051 | 0.0642 | 0.1161 | 0.1556 | 1.6818 | 0.1719 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0083 | 0.1034 | 0.0590 | 0.1506 | 1.4886 | 0.1472 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0167 | 0.2083 | 0.1123 | 0.1462 | 1.6901 | 0.1834 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0039 | 0.0488 | 0.0865 | 0.1557 | 1.5869 | 0.1595 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0083 | 0.1034 | 0.1014 | 0.1559 | 1.6386 | 0.1691 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.1171 | 0.0094 | 0.0990 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
