# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
| `ppo_swish_command_conditioned_step0` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0005 | NA | 0.0002 | 0.1521 | 0.0153 | 0.0314 |
| `ppo_swish_command_conditioned_step0` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0023 | NA | 0.0111 | 0.1557 | 0.0152 | 0.0315 |
| `ppo_swish_command_conditioned_step0` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0006 | NA | 0.0001 | 0.1511 | 0.0155 | 0.0317 |
| `ppo_swish_command_conditioned_step0` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | -0.3456 | NA | 0.2072 | 0.0504 | 0.9111 | 0.1058 |
| `ppo_swish_command_conditioned_step0` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0023 | NA | 0.0243 | 0.1507 | 0.0148 | 0.0345 |
| `ppo_swish_command_conditioned_step0` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 53 | `fall_or_nan` | -0.2773 | NA | 0.0661 | 0.0634 | 1.0749 | 0.1831 |
| `ppo_swish_command_conditioned_step0` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0018 | NA | 0.0215 | 0.1562 | 0.0191 | 0.0350 |
| `ppo_swish_command_conditioned_step0` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0008 | NA | 0.0031 | 0.1559 | 0.0144 | 0.0296 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_swish_command_conditioned_step0` | 8 | 2 | 6 | 389.1250 | 53 | 500 | NA | -0.0783 | 0.0417 | 0.1294 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
