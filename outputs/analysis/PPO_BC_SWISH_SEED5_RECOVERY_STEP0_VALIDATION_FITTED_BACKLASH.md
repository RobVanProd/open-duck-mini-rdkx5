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
| `ppo_swish_seed5_recovery_step0` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0436 | 0.5455 | 0.1022 | 0.1520 | 3.8990 | 0.2657 |
| `ppo_swish_seed5_recovery_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0373 | 0.4667 | 0.1006 | 0.1556 | 3.8474 | 0.2685 |
| `ppo_swish_seed5_recovery_step0` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0453 | 0.5661 | 0.1017 | 0.1509 | 3.8485 | 0.2634 |
| `ppo_swish_seed5_recovery_step0` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0387 | 0.4838 | 0.1018 | 0.1555 | 3.9066 | 0.2690 |
| `ppo_swish_seed5_recovery_step0` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0417 | 0.5208 | 0.0992 | 0.1506 | 3.8829 | 0.2702 |
| `ppo_swish_seed5_recovery_step0` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 75 | `fall_or_nan` | -0.1893 | -2.3662 | 0.0941 | 0.0777 | 4.0999 | 0.3073 |
| `ppo_swish_seed5_recovery_step0` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0383 | 0.4787 | 0.0986 | 0.1557 | 3.8722 | 0.2725 |
| `ppo_swish_seed5_recovery_step0` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0401 | 0.5012 | 0.1051 | 0.1555 | 3.8669 | 0.2697 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_swish_seed5_recovery_step0` | 8 | 1 | 7 | 446.8750 | 75 | 500 | 0.1496 | 0.0120 | 0.1004 | 0.1442 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
