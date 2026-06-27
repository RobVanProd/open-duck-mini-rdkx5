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
| `live_oracle_dagger_iter1` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0482 | 0.6025 | 0.1025 | 0.1520 | 3.6963 | 0.2647 |
| `live_oracle_dagger_iter1` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0443 | 0.5533 | 0.1003 | 0.1556 | 3.7287 | 0.2660 |
| `live_oracle_dagger_iter1` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0483 | 0.6036 | 0.1016 | 0.1509 | 3.6903 | 0.2644 |
| `live_oracle_dagger_iter1` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0441 | 0.5508 | 0.1009 | 0.1552 | 3.6815 | 0.2625 |
| `live_oracle_dagger_iter1` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0465 | 0.5807 | 0.1014 | 0.1506 | 3.7221 | 0.2624 |
| `live_oracle_dagger_iter1` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 74 | `fall_or_nan` | -0.2043 | -2.5536 | 0.0905 | 0.0674 | 3.2508 | 0.2666 |
| `live_oracle_dagger_iter1` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0443 | 0.5539 | 0.1048 | 0.1557 | 3.7024 | 0.2627 |
| `live_oracle_dagger_iter1` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0469 | 0.5862 | 0.1007 | 0.1559 | 3.6833 | 0.2600 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_dagger_iter1` | 8 | 1 | 7 | 665.5000 | 74 | 750 | 0.1847 | 0.0148 | 0.1003 | 0.1429 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
