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
| `ppo_warmstart_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0432 | 0.5399 | 0.0996 | 0.1520 | 3.7014 | 0.2553 |
| `ppo_warmstart_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4509 | 0.1002 | 0.1556 | 3.6651 | 0.2531 |
| `ppo_warmstart_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0428 | 0.5349 | 0.1019 | 0.1509 | 3.6201 | 0.2522 |
| `ppo_warmstart_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0366 | 0.4577 | 0.1028 | 0.1562 | 3.6804 | 0.2583 |
| `ppo_warmstart_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0409 | 0.5113 | 0.0997 | 0.1506 | 3.7078 | 0.2570 |
| `ppo_warmstart_step0` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0429 | 0.5365 | 0.0977 | 0.1462 | 3.6200 | 0.2583 |
| `ppo_warmstart_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0353 | 0.4417 | 0.0985 | 0.1545 | 3.6823 | 0.2523 |
| `ppo_warmstart_step0` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0386 | 0.4822 | 0.0999 | 0.1559 | 3.6604 | 0.2570 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_warmstart_step0` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4944 | 0.0396 | 0.1000 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
