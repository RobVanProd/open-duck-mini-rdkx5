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
| `ppo_loc_dagger7_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0340 | 0.4254 | 0.0610 | 0.1536 | 3.8272 | 0.2393 |
| `ppo_loc_dagger7_step0` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0115 | 0.1442 | 0.0008 | 0.0855 | 3.6231 | 0.3329 |
| `ppo_loc_dagger7_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0329 | 0.4114 | 0.0614 | 0.1525 | 3.8316 | 0.2454 |
| `ppo_loc_dagger7_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0285 | 0.3566 | 0.0591 | 0.1587 | 3.8211 | 0.2366 |
| `ppo_loc_dagger7_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0289 | 0.3618 | 0.0652 | 0.1515 | 3.7830 | 0.2459 |
| `ppo_loc_dagger7_step0` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0342 | 0.4272 | 0.0625 | 0.1469 | 3.7863 | 0.2431 |
| `ppo_loc_dagger7_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0221 | 0.2766 | 0.0623 | 0.1587 | 3.8191 | 0.2409 |
| `ppo_loc_dagger7_step0` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0208 | 0.2600 | 0.0012 | 0.0770 | 4.0311 | 0.3052 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_dagger7_step0` | 8 | 2 | 6 | 383.0000 | 32 | 500 | 0.3329 | 0.0266 | 0.0467 | 0.1356 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
