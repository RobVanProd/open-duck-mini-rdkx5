# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.04`
bridge_mode: `vanilla`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 1, 2, 3]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `v5_phase1` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0018 | 0.0452 | 0.0827 | 0.1537 | 0.2467 | 0.0607 |
| `v5_phase1` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.1549 | -3.8716 | 0.0008 | 0.0884 | 2.0085 | 0.2060 |
| `v5_phase1` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0033 | 0.0821 | 0.0821 | 0.1526 | 0.2489 | 0.0603 |
| `v5_phase1` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0088 | -0.2207 | 0.1266 | 0.1549 | 0.2340 | 0.0609 |
| `v7_anchor` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0013 | 0.0325 | 0.0786 | 0.1539 | 0.4096 | 0.0539 |
| `v7_anchor` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | -0.1641 | -4.1034 | 0.0044 | 0.1059 | 1.8394 | 0.1766 |
| `v7_anchor` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0019 | 0.0484 | 0.0683 | 0.1526 | 0.3520 | 0.0571 |
| `v7_anchor` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0090 | -0.2249 | 0.1160 | 0.1558 | 0.2412 | 0.0547 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v5_phase1` | 4 | 1 | 3 | 196.0000 | 34 | 250 | -0.9913 | -0.0397 | 0.0731 | 0.1374 |
| `v7_anchor` | 4 | 1 | 3 | 196.2500 | 35 | 250 | -1.0619 | -0.0425 | 0.0668 | 0.1421 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
