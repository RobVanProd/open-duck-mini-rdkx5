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
| `ppo_loc_bc` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0391 | 0.4883 | 0.0981 | 0.1520 | 3.9230 | 0.2653 |
| `ppo_loc_bc` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4517 | 0.0961 | 0.1556 | 3.8735 | 0.2678 |
| `ppo_loc_bc` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0419 | 0.5234 | 0.0992 | 0.1509 | 3.8384 | 0.2645 |
| `ppo_loc_bc` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0328 | 0.4100 | 0.1020 | 0.1554 | 3.8763 | 0.2650 |
| `ppo_loc_bc` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0395 | 0.4942 | 0.0970 | 0.1506 | 3.8650 | 0.2641 |
| `ppo_loc_bc` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0412 | 0.5156 | 0.0962 | 0.1462 | 3.9028 | 0.2697 |
| `ppo_loc_bc` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4518 | 0.0962 | 0.1557 | 3.8905 | 0.2703 |
| `ppo_loc_bc` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0379 | 0.4733 | 0.0965 | 0.1554 | 3.9250 | 0.2670 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_bc` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4761 | 0.0381 | 0.0977 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
