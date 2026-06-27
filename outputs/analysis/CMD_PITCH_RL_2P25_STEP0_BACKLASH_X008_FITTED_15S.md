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
| `cmd_pitch_rl_2p25_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0366 | 0.4575 | 0.1180 | 0.1520 | 2.1112 | 0.1997 |
| `cmd_pitch_rl_2p25_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0335 | 0.4189 | 0.1165 | 0.1556 | 2.1074 | 0.1966 |
| `cmd_pitch_rl_2p25_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0356 | 0.4450 | 0.1214 | 0.1509 | 2.1318 | 0.1996 |
| `cmd_pitch_rl_2p25_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0293 | 0.3661 | 0.1209 | 0.1554 | 2.1254 | 0.1998 |
| `cmd_pitch_rl_2p25_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0361 | 0.4510 | 0.1173 | 0.1506 | 2.1770 | 0.1927 |
| `cmd_pitch_rl_2p25_step0` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0369 | 0.4608 | 0.1189 | 0.1462 | 2.1174 | 0.2013 |
| `cmd_pitch_rl_2p25_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0327 | 0.4084 | 0.1160 | 0.1557 | 2.1356 | 0.1931 |
| `cmd_pitch_rl_2p25_step0` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0374 | 0.4674 | 0.1177 | 0.1559 | 2.0841 | 0.1955 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_pitch_rl_2p25_step0` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4344 | 0.0348 | 0.1183 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
