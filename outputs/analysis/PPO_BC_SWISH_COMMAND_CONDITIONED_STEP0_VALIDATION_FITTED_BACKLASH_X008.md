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
| `ppo_swish_command_conditioned_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0427 | 0.5341 | 0.0923 | 0.1520 | 3.7460 | 0.2630 |
| `ppo_swish_command_conditioned_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0394 | 0.4927 | 0.0908 | 0.1556 | 3.7642 | 0.2556 |
| `ppo_swish_command_conditioned_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0463 | 0.5793 | 0.0947 | 0.1509 | 3.7610 | 0.2644 |
| `ppo_swish_command_conditioned_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0377 | 0.4709 | 0.0967 | 0.1559 | 3.7889 | 0.2652 |
| `ppo_swish_command_conditioned_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0415 | 0.5185 | 0.0978 | 0.1506 | 3.7593 | 0.2641 |
| `ppo_swish_command_conditioned_step0` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0443 | 0.5534 | 0.0938 | 0.1462 | 3.7935 | 0.2708 |
| `ppo_swish_command_conditioned_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0383 | 0.4790 | 0.0954 | 0.1557 | 3.7880 | 0.2670 |
| `ppo_swish_command_conditioned_step0` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0400 | 0.4998 | 0.0962 | 0.1559 | 3.7727 | 0.2602 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_swish_command_conditioned_step0` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.5160 | 0.0413 | 0.0947 | 0.1529 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
