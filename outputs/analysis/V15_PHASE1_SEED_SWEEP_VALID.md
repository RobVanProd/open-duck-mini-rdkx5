# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
bridge_mode: `vanilla`
duration_s: `5.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `2026_06_24_100138_337920` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0009 | 0.0112 | 0.0819 | 0.1534 | 0.0948 | 0.0539 |
| `2026_06_24_100138_337920` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.1037 | -1.2957 | 0.0055 | 0.0900 | 0.7089 | 0.1983 |
| `2026_06_24_100138_337920` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0027 | 0.0336 | 0.0553 | 0.1526 | 0.0814 | 0.0505 |
| `2026_06_24_100138_337920` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0044 | -0.0551 | 0.0708 | 0.1574 | 0.0908 | 0.0495 |
| `2026_06_24_100138_337920` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0053 | 0.0659 | 0.0620 | 0.1513 | 0.0820 | 0.0528 |
| `2026_06_24_100138_337920` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 44 | `fall_or_nan` | -0.3632 | -4.5403 | 0.0468 | 0.0416 | 1.0609 | 0.1669 |
| `2026_06_24_100138_337920` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0039 | -0.0484 | 0.0439 | 0.1581 | 0.0891 | 0.0574 |
| `2026_06_24_100138_337920` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.0094 | -0.1175 | 0.0501 | 0.0748 | 0.9700 | 0.3991 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `2026_06_24_100138_337920` | 8 | 3 | 5 | 170.1250 | 33 | 250 | -0.7433 | -0.0595 | 0.0520 | 0.1224 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
