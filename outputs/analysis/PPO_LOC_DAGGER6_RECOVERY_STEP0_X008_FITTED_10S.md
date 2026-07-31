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
| `ppo_step0_d6` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0317 | 0.3962 | 0.0647 | 0.1536 | 3.7774 | 0.2327 |
| `ppo_step0_d6` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0054 | 0.0678 | 0.0013 | 0.0879 | 3.3201 | 0.3134 |
| `ppo_step0_d6` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0333 | 0.4163 | 0.0723 | 0.1525 | 3.7485 | 0.2372 |
| `ppo_step0_d6` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0290 | 0.3619 | 0.0695 | 0.1577 | 3.7522 | 0.2390 |
| `ppo_step0_d6` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0281 | 0.3514 | 0.0676 | 0.1516 | 3.7378 | 0.2377 |
| `ppo_step0_d6` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 64 | `fall_or_nan` | -0.2300 | -2.8744 | 0.0861 | 0.0672 | 3.3184 | 0.2879 |
| `ppo_step0_d6` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0245 | 0.3064 | 0.0722 | 0.1578 | 3.7701 | 0.2365 |
| `ppo_step0_d6` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0183 | 0.2293 | 0.0011 | 0.0823 | 3.3353 | 0.3148 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0_d6` | 8 | 3 | 5 | 328.6250 | 32 | 500 | -0.0931 | -0.0075 | 0.0544 | 0.1263 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
