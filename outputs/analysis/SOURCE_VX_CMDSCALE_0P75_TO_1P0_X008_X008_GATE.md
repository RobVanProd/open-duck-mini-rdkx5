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
| `cmdscale_0p75_to_1p0_x008` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0425 | 0.5315 | 0.1030 | 0.1520 | 3.8063 | 0.2648 |
| `cmdscale_0p75_to_1p0_x008` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0385 | 0.4816 | 0.0984 | 0.1556 | 3.8244 | 0.2651 |
| `cmdscale_0p75_to_1p0_x008` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0453 | 0.5660 | 0.1019 | 0.1509 | 3.7977 | 0.2619 |
| `cmdscale_0p75_to_1p0_x008` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0387 | 0.4843 | 0.0985 | 0.1562 | 3.8475 | 0.2696 |
| `cmdscale_0p75_to_1p0_x008` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0418 | 0.5230 | 0.1032 | 0.1506 | 3.8309 | 0.2650 |
| `cmdscale_0p75_to_1p0_x008` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0454 | 0.5676 | 0.0967 | 0.1463 | 3.7988 | 0.2719 |
| `cmdscale_0p75_to_1p0_x008` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0387 | 0.4831 | 0.0986 | 0.1557 | 3.8086 | 0.2662 |
| `cmdscale_0p75_to_1p0_x008` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0419 | 0.5233 | 0.1037 | 0.1554 | 3.8601 | 0.2654 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmdscale_0p75_to_1p0_x008` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.5201 | 0.0416 | 0.1005 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
