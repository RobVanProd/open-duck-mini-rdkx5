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
| `dagger3_ppo_shape` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0420 | 0.5247 | 0.1026 | 0.1520 | 3.8409 | 0.2634 |
| `dagger3_ppo_shape` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0379 | 0.4735 | 0.0943 | 0.1556 | 3.8010 | 0.2570 |
| `dagger3_ppo_shape` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0435 | 0.5432 | 0.1045 | 0.1509 | 3.8210 | 0.2624 |
| `dagger3_ppo_shape` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4508 | 0.1037 | 0.1557 | 3.7842 | 0.2591 |
| `dagger3_ppo_shape` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0407 | 0.5093 | 0.0942 | 0.1506 | 3.8162 | 0.2624 |
| `dagger3_ppo_shape` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0436 | 0.5449 | 0.0975 | 0.1462 | 3.8099 | 0.2684 |
| `dagger3_ppo_shape` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4516 | 0.0968 | 0.1557 | 3.7994 | 0.2628 |
| `dagger3_ppo_shape` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0372 | 0.4648 | 0.1026 | 0.1559 | 3.8345 | 0.2571 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dagger3_ppo_shape` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4953 | 0.0396 | 0.0995 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
