# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
bridge_mode: `vanilla`
duration_s: `5.0`
seeds: `[0, 1, 2, 3]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `v5_recovery` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 69 | `fall_or_nan` | 0.2222 | 2.7775 | 1.2482 | 0.0430 | 1.7792 | 0.1664 |
| `v5_recovery` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.0350 | -0.4371 | 0.0050 | 0.0848 | 1.6385 | 0.1824 |
| `v5_recovery` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0083 | 0.1035 | 0.3390 | 0.1461 | 0.2043 | 0.0831 |
| `v5_recovery` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0021 | -0.0261 | 0.3052 | 0.1471 | 0.2227 | 0.0719 |
| `v15_phase1` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0009 | 0.0112 | 0.0819 | 0.1534 | 0.0948 | 0.0539 |
| `v15_phase1` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.1037 | -1.2957 | 0.0055 | 0.0900 | 0.7089 | 0.1983 |
| `v15_phase1` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0027 | 0.0336 | 0.0553 | 0.1526 | 0.0814 | 0.0505 |
| `v15_phase1` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0044 | -0.0551 | 0.0708 | 0.1574 | 0.0908 | 0.0495 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v5_recovery` | 4 | 2 | 2 | 150.7500 | 34 | 250 | 0.6045 | 0.0484 | 0.4744 | 0.1052 |
| `v15_phase1` | 4 | 1 | 3 | 195.7500 | 33 | 250 | -0.3265 | -0.0261 | 0.0534 | 0.1384 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
