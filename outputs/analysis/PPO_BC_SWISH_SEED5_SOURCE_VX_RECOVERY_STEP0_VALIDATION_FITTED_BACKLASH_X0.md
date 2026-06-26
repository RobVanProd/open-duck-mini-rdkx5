# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
| `ppo_swish_seed5_source_vx_recovery_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0441 | NA | 0.0982 | 0.1520 | 3.8316 | 0.2649 |
| `ppo_swish_seed5_source_vx_recovery_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0394 | NA | 0.1008 | 0.1556 | 3.8709 | 0.2638 |
| `ppo_swish_seed5_source_vx_recovery_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0461 | NA | 0.0988 | 0.1509 | 3.8150 | 0.2649 |
| `ppo_swish_seed5_source_vx_recovery_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0388 | NA | 0.1054 | 0.1561 | 3.8347 | 0.2645 |
| `ppo_swish_seed5_source_vx_recovery_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0413 | NA | 0.1017 | 0.1506 | 3.8093 | 0.2666 |
| `ppo_swish_seed5_source_vx_recovery_step0` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0450 | NA | 0.0974 | 0.1463 | 3.7678 | 0.2687 |
| `ppo_swish_seed5_source_vx_recovery_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0377 | NA | 0.1002 | 0.1557 | 3.8682 | 0.2661 |
| `ppo_swish_seed5_source_vx_recovery_step0` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0400 | NA | 0.1031 | 0.1559 | 3.8706 | 0.2659 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_swish_seed5_source_vx_recovery_step0` | 8 | 0 | 8 | 500.0000 | 500 | 500 | NA | 0.0415 | 0.1007 | 0.1529 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
