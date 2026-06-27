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
| `behavior_preserving_smoke` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0211 | 0.2638 | 0.1150 | 0.1520 | 2.1920 | 0.1719 |
| `behavior_preserving_smoke` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | -0.0014 | -0.0179 | 0.0124 | 0.1556 | 0.5553 | 0.0631 |
| `behavior_preserving_smoke` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0005 | 0.0062 | 0.0126 | 0.1509 | 0.6743 | 0.0612 |
| `behavior_preserving_smoke` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 74 | `fall_or_nan` | -0.2708 | -3.3845 | 0.2264 | 0.0684 | 1.4815 | 0.1446 |
| `behavior_preserving_smoke` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0265 | 0.3316 | 0.1129 | 0.1506 | 2.2024 | 0.1735 |
| `behavior_preserving_smoke` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0244 | 0.3045 | 0.1148 | 0.1458 | 2.1958 | 0.1743 |
| `behavior_preserving_smoke` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0232 | 0.2895 | 0.1191 | 0.1557 | 2.1533 | 0.1758 |
| `behavior_preserving_smoke` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0001 | 0.0006 | 0.0140 | 0.1559 | 0.7172 | 0.0616 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `behavior_preserving_smoke` | 8 | 1 | 7 | 665.5000 | 74 | 750 | -0.2758 | -0.0221 | 0.0909 | 0.1419 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
