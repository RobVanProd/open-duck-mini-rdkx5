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
| `pitch_chain_4p3_ppo_shape_rate_student` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0423 | 0.5287 | 0.0993 | 0.1520 | 3.6195 | 0.2527 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0359 | 0.4484 | 0.0991 | 0.1556 | 3.7059 | 0.2554 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0425 | 0.5308 | 0.0993 | 0.1509 | 3.6418 | 0.2551 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4518 | 0.1033 | 0.1562 | 3.6564 | 0.2539 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0393 | 0.4918 | 0.0967 | 0.1506 | 3.7024 | 0.2561 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0429 | 0.5360 | 0.0956 | 0.1462 | 3.6035 | 0.2529 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0360 | 0.4503 | 0.0985 | 0.1557 | 3.6642 | 0.2516 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0394 | 0.4921 | 0.1007 | 0.1557 | 3.6449 | 0.2533 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pitch_chain_4p3_ppo_shape_rate_student` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4913 | 0.0393 | 0.0991 | 0.1529 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
