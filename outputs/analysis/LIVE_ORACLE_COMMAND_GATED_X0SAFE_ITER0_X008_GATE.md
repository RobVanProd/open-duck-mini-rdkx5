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

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `live_oracle_command_gated_x0safe_iter0` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0468 | 0.5849 | 0.1002 | 0.1520 | 3.6293 | 0.2605 |
| `live_oracle_command_gated_x0safe_iter0` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0440 | 0.5497 | 0.0986 | 0.1556 | 3.6645 | 0.2628 |
| `live_oracle_command_gated_x0safe_iter0` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0489 | 0.6116 | 0.0990 | 0.1509 | 3.6195 | 0.2601 |
| `live_oracle_command_gated_x0safe_iter0` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0432 | 0.5402 | 0.1002 | 0.1546 | 3.6621 | 0.2641 |
| `live_oracle_command_gated_x0safe_iter0` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0451 | 0.5633 | 0.1003 | 0.1506 | 3.6791 | 0.2645 |
| `live_oracle_command_gated_x0safe_iter0` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0458 | 0.5724 | 0.0978 | 0.1462 | 3.6534 | 0.2612 |
| `live_oracle_command_gated_x0safe_iter0` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0410 | 0.5126 | 0.0996 | 0.1557 | 3.6537 | 0.2649 |
| `live_oracle_command_gated_x0safe_iter0` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0444 | 0.5553 | 0.0987 | 0.1559 | 3.6661 | 0.2665 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_command_gated_x0safe_iter0` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.5613 | 0.0449 | 0.0993 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
