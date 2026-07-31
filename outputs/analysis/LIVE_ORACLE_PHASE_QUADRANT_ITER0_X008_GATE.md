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
| `live_oracle_phase_quadrant_iter0_x008` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0356 | 0.4444 | 0.1099 | 0.1520 | 4.8992 | 0.2711 |
| `live_oracle_phase_quadrant_iter0_x008` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0394 | 0.4926 | 0.1092 | 0.1548 | 4.8099 | 0.2706 |
| `live_oracle_phase_quadrant_iter0_x008` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 665 | `fall_or_nan` | 0.0161 | 0.2009 | 0.1180 | 0.0774 | 5.2400 | 0.2635 |
| `live_oracle_phase_quadrant_iter0_x008` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0301 | 0.3763 | 0.1117 | 0.1531 | 4.7929 | 0.2696 |
| `live_oracle_phase_quadrant_iter0_x008` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0360 | 0.4501 | 0.1029 | 0.1506 | 4.8211 | 0.2665 |
| `live_oracle_phase_quadrant_iter0_x008` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0399 | 0.4991 | 0.1068 | 0.1463 | 4.7127 | 0.2687 |
| `live_oracle_phase_quadrant_iter0_x008` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0327 | 0.4093 | 0.1108 | 0.1465 | 4.9416 | 0.2653 |
| `live_oracle_phase_quadrant_iter0_x008` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0370 | 0.4620 | 0.1056 | 0.1536 | 4.6558 | 0.2696 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_phase_quadrant_iter0_x008` | 8 | 1 | 7 | 739.3750 | 665 | 750 | 0.4168 | 0.0333 | 0.1094 | 0.1418 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
