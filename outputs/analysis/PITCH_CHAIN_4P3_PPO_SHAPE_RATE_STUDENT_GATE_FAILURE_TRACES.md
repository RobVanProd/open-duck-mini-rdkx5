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
trace_seeds: `[1, 4]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `pitch_chain_4p3_ppo_shape_rate_student` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0359 | 0.4484 | 0.0991 | 0.1556 | 3.7059 | 0.2554 |
| `pitch_chain_4p3_ppo_shape_rate_student` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0393 | 0.4918 | 0.0967 | 0.1506 | 3.7024 | 0.2561 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pitch_chain_4p3_ppo_shape_rate_student` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4701 | 0.0376 | 0.0979 | 0.1531 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
