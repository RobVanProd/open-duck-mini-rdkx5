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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `ppo_loc_dagger7` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0321 | 0.4017 | 0.0593 | 0.1536 | 3.8260 | 0.2371 |
| `ppo_loc_dagger7` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0115 | 0.1443 | 0.0008 | 0.0855 | 3.6231 | 0.3329 |
| `ppo_loc_dagger7` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0328 | 0.4104 | 0.0620 | 0.1525 | 3.8268 | 0.2380 |
| `ppo_loc_dagger7` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0287 | 0.3584 | 0.0599 | 0.1585 | 3.8063 | 0.2386 |
| `ppo_loc_dagger7` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0288 | 0.3602 | 0.0656 | 0.1515 | 3.8281 | 0.2408 |
| `ppo_loc_dagger7` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0342 | 0.4279 | 0.0619 | 0.1469 | 3.8133 | 0.2476 |
| `ppo_loc_dagger7` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0238 | 0.2971 | 0.0630 | 0.1584 | 3.8327 | 0.2404 |
| `ppo_loc_dagger7` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0219 | 0.2742 | 0.0006 | 0.0762 | 4.0282 | 0.3052 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_dagger7` | 8 | 2 | 6 | 383.0000 | 32 | 500 | 0.3343 | 0.0267 | 0.0467 | 0.1354 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
