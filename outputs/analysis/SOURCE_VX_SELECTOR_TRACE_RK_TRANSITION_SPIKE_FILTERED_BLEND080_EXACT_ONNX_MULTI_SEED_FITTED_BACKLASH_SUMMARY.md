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
| `rk_transition_filtered` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0466 | 0.5820 | 0.0967 | 0.1520 | 4.6244 | 0.2675 |
| `rk_transition_filtered` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0441 | 0.5515 | 0.0964 | 0.1556 | 4.7332 | 0.2700 |
| `rk_transition_filtered` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0485 | 0.6065 | 0.0975 | 0.1509 | 4.6839 | 0.2724 |
| `rk_transition_filtered` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0394 | 0.4921 | 0.0961 | 0.1545 | 4.6539 | 0.2696 |
| `rk_transition_filtered` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0470 | 0.5876 | 0.0934 | 0.1506 | 4.7790 | 0.2782 |
| `rk_transition_filtered` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0471 | 0.5882 | 0.0979 | 0.1462 | 4.6816 | 0.2712 |
| `rk_transition_filtered` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0424 | 0.5295 | 0.0962 | 0.1557 | 4.6340 | 0.2723 |
| `rk_transition_filtered` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0445 | 0.5558 | 0.0970 | 0.1559 | 4.6360 | 0.2759 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rk_transition_filtered` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.5617 | 0.0449 | 0.0964 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
