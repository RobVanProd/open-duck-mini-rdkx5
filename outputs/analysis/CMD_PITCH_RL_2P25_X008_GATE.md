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
| `cmd_pitch_rl_2p25` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0355 | 0.4432 | 0.1200 | 0.1520 | 2.1734 | 0.1979 |
| `cmd_pitch_rl_2p25` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0352 | 0.4404 | 0.1204 | 0.1556 | 2.1326 | 0.1969 |
| `cmd_pitch_rl_2p25` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0386 | 0.4821 | 0.1182 | 0.1509 | 2.1163 | 0.2008 |
| `cmd_pitch_rl_2p25` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0273 | 0.3415 | 0.1249 | 0.1554 | 2.1112 | 0.1982 |
| `cmd_pitch_rl_2p25` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0358 | 0.4469 | 0.1121 | 0.1506 | 2.1305 | 0.1937 |
| `cmd_pitch_rl_2p25` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0316 | 0.3951 | 0.1205 | 0.1462 | 2.1731 | 0.1996 |
| `cmd_pitch_rl_2p25` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0331 | 0.4133 | 0.1139 | 0.1557 | 2.1253 | 0.1896 |
| `cmd_pitch_rl_2p25` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4510 | 0.1159 | 0.1559 | 2.1342 | 0.1936 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_pitch_rl_2p25` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4267 | 0.0341 | 0.1182 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
