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
| `v16_81920` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0062 | 0.0780 | 0.3234 | 0.1484 | 0.2457 | 0.0808 |
| `v16_81920` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | -0.0448 | -0.5597 | 0.0036 | 0.0799 | 1.4773 | 0.1822 |
| `v16_81920` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0074 | 0.0919 | 0.2720 | 0.1480 | 0.2702 | 0.0770 |
| `v16_81920` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0031 | -0.0390 | 0.2792 | 0.1478 | 0.1931 | 0.0704 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v16_81920` | 4 | 1 | 3 | 196.2500 | 35 | 250 | -0.1072 | -0.0086 | 0.2196 | 0.1310 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
