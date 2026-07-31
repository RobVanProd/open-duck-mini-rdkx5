# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain`
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
| `dagger5` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0225 | 0.2808 | 0.0536 | 0.1536 | 3.6946 | 0.2265 |
| `dagger5` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0043 | 0.0536 | 0.0005 | 0.0848 | 2.5565 | 0.2746 |
| `dagger5` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0255 | 0.3189 | 0.0503 | 0.1525 | 3.6566 | 0.2245 |
| `dagger5` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0203 | 0.2536 | 0.0661 | 0.1579 | 3.7474 | 0.2239 |
| `dagger5` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0225 | 0.2807 | 0.0604 | 0.1515 | 3.7202 | 0.2247 |
| `dagger5` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0279 | 0.3492 | 0.0553 | 0.1468 | 3.8066 | 0.2263 |
| `dagger5` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0199 | 0.2491 | 0.0632 | 0.1582 | 3.7867 | 0.2232 |
| `dagger5` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0295 | 0.3682 | 0.0335 | 0.0785 | 3.2176 | 0.3073 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dagger5` | 8 | 2 | 6 | 383.2500 | 33 | 500 | 0.2693 | 0.0215 | 0.0479 | 0.1355 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
