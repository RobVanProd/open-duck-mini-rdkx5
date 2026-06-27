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
| `cmd_pitch_rl_2p25_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0363 | 0.4540 | 0.1174 | 0.1520 | 2.1101 | 0.1984 |
| `cmd_pitch_rl_2p25_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0336 | 0.4196 | 0.1130 | 0.1556 | 2.1064 | 0.1963 |
| `cmd_pitch_rl_2p25_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0365 | 0.4565 | 0.1239 | 0.1509 | 2.1502 | 0.2013 |
| `cmd_pitch_rl_2p25_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0281 | 0.3512 | 0.1217 | 0.1554 | 2.0844 | 0.1974 |
| `cmd_pitch_rl_2p25_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0374 | 0.4670 | 0.1143 | 0.1506 | 2.1523 | 0.1896 |
| `cmd_pitch_rl_2p25_step0` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0369 | 0.4611 | 0.1188 | 0.1462 | 2.1527 | 0.1999 |
| `cmd_pitch_rl_2p25_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0316 | 0.3951 | 0.1142 | 0.1557 | 2.1203 | 0.1904 |
| `cmd_pitch_rl_2p25_step0` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0376 | 0.4702 | 0.1159 | 0.1559 | 2.0803 | 0.1930 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_pitch_rl_2p25_step0` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4343 | 0.0347 | 0.1174 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
