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
| `ppo_loc_d6` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0324 | 0.4045 | 0.0667 | 0.1536 | 3.7629 | 0.2369 |
| `ppo_loc_d6` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0054 | 0.0676 | 0.0013 | 0.0880 | 3.3207 | 0.3134 |
| `ppo_loc_d6` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0312 | 0.3899 | 0.0639 | 0.1525 | 3.7573 | 0.2355 |
| `ppo_loc_d6` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0278 | 0.3475 | 0.0696 | 0.1576 | 3.7441 | 0.2379 |
| `ppo_loc_d6` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0290 | 0.3628 | 0.0725 | 0.1516 | 3.7309 | 0.2388 |
| `ppo_loc_d6` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 64 | `fall_or_nan` | -0.2296 | -2.8695 | 0.0861 | 0.0678 | 3.3188 | 0.2879 |
| `ppo_loc_d6` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0243 | 0.3037 | 0.0715 | 0.1576 | 3.7632 | 0.2382 |
| `ppo_loc_d6` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0176 | 0.2198 | 0.0012 | 0.0825 | 3.5410 | 0.3148 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_d6` | 8 | 3 | 5 | 328.6250 | 32 | 500 | -0.0967 | -0.0077 | 0.0541 | 0.1264 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
