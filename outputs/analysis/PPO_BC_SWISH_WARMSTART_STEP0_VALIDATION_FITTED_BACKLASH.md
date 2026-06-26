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
| `ppo_swish_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0458 | 0.5721 | 0.1034 | 0.1520 | 3.7157 | 0.2586 |
| `ppo_swish_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0396 | 0.4948 | 0.1007 | 0.1556 | 3.7928 | 0.2644 |
| `ppo_swish_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0458 | 0.5723 | 0.0996 | 0.1509 | 3.7649 | 0.2584 |
| `ppo_swish_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0371 | 0.4642 | 0.1011 | 0.1554 | 3.7266 | 0.2629 |
| `ppo_swish_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0433 | 0.5413 | 0.1016 | 0.1506 | 3.7883 | 0.2620 |
| `ppo_swish_step0` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 74 | `fall_or_nan` | -0.1976 | -2.4697 | 0.0895 | 0.0717 | 3.4393 | 0.2874 |
| `ppo_swish_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0383 | 0.4791 | 0.0994 | 0.1557 | 3.7968 | 0.2682 |
| `ppo_swish_step0` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0399 | 0.4989 | 0.1085 | 0.1547 | 3.8002 | 0.2652 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_swish_step0` | 8 | 1 | 7 | 446.7500 | 74 | 500 | 0.1441 | 0.0115 | 0.1005 | 0.1433 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
