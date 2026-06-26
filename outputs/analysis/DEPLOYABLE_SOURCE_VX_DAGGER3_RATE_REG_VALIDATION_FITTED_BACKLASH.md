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
| `dagger3_rate_reg` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0446 | 0.5571 | 0.0976 | 0.1520 | 3.7792 | 0.2656 |
| `dagger3_rate_reg` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0409 | 0.5110 | 0.1032 | 0.1556 | 3.7850 | 0.2650 |
| `dagger3_rate_reg` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0455 | 0.5689 | 0.1007 | 0.1509 | 3.8254 | 0.2675 |
| `dagger3_rate_reg` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0405 | 0.5065 | 0.1021 | 0.1550 | 3.7936 | 0.2623 |
| `dagger3_rate_reg` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0423 | 0.5285 | 0.1049 | 0.1506 | 3.8180 | 0.2645 |
| `dagger3_rate_reg` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0406 | 0.5081 | 0.0982 | 0.1462 | 3.8488 | 0.2767 |
| `dagger3_rate_reg` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0406 | 0.5071 | 0.1008 | 0.1557 | 3.8101 | 0.2673 |
| `dagger3_rate_reg` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0414 | 0.5170 | 0.1063 | 0.1558 | 3.7121 | 0.2686 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dagger3_rate_reg` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.5255 | 0.0420 | 0.1017 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
