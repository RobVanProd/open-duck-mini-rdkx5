# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[1, 4]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `ppo_warmstart_progress_failure_640` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | -0.0007 | -0.0092 | 0.0539 | 0.1556 | 1.2083 | 0.1199 |
| `ppo_warmstart_progress_failure_640` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0033 | 0.0417 | 0.0500 | 0.1506 | 1.0734 | 0.1016 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_warmstart_progress_failure_640` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.0162 | 0.0013 | 0.0519 | 0.1531 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
