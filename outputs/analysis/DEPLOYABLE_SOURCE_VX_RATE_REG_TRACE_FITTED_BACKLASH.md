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
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `dagger2_rate_reg` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0367 | 0.4592 | 0.0953 | 0.1520 | 3.6419 | 0.2461 |
| `dagger2_rate_reg` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0357 | 0.4463 | 0.1006 | 0.1556 | 3.6824 | 0.2424 |
| `dagger2_rate_reg` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0414 | 0.5173 | 0.1003 | 0.1509 | 3.6397 | 0.2446 |
| `dagger2_rate_reg` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0289 | 0.3616 | 0.0991 | 0.1552 | 3.6396 | 0.2458 |
| `dagger2_rate_reg` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0374 | 0.4673 | 0.1037 | 0.1506 | 3.6223 | 0.2465 |
| `dagger2_rate_reg` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0411 | 0.5143 | 0.0976 | 0.1462 | 3.6737 | 0.2472 |
| `dagger2_rate_reg` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0339 | 0.4240 | 0.0983 | 0.1557 | 3.6445 | 0.2425 |
| `dagger2_rate_reg` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0360 | 0.4503 | 0.1020 | 0.1559 | 3.6172 | 0.2419 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dagger2_rate_reg` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4550 | 0.0364 | 0.0996 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
