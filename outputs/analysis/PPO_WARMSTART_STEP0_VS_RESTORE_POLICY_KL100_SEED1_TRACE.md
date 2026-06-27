# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[1]`
trace_seeds: `[1]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `ppo_warmstart_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0361 | 0.4509 | 0.1002 | 0.1556 | 3.6651 | 0.2531 |
| `ppo_warmstart_restore_policy_kl100_640` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | -0.0006 | -0.0078 | 0.0502 | 0.1556 | 1.2197 | 0.1150 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_warmstart_step0` | 1 | 0 | 1 | 500.0000 | 500 | 500 | 0.4509 | 0.0361 | 0.1002 | 0.1556 |
| `ppo_warmstart_restore_policy_kl100_640` | 1 | 0 | 1 | 500.0000 | 500 | 500 | -0.0078 | -0.0006 | 0.0502 | 0.1556 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
