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
| `ppo_step1040_d6` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0119 | 0.1489 | 0.0546 | 0.1537 | 3.6779 | 0.2068 |
| `ppo_step1040_d6` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 29 | `fall_or_nan` | 0.0236 | 0.2953 | 0.0006 | 0.0875 | 3.0656 | 0.3225 |
| `ppo_step1040_d6` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0121 | 0.1507 | 0.0552 | 0.1525 | 3.6686 | 0.2046 |
| `ppo_step1040_d6` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0073 | 0.0919 | 0.0570 | 0.1598 | 3.6578 | 0.2065 |
| `ppo_step1040_d6` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0127 | 0.1589 | 0.0473 | 0.1515 | 3.6977 | 0.2069 |
| `ppo_step1040_d6` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0147 | 0.1832 | 0.0549 | 0.1469 | 3.6659 | 0.2101 |
| `ppo_step1040_d6` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0094 | 0.1179 | 0.0493 | 0.1587 | 3.6740 | 0.2069 |
| `ppo_step1040_d6` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | -0.0035 | -0.0434 | 0.0197 | 0.0702 | 3.5484 | 0.3949 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step1040_d6` | 8 | 2 | 6 | 382.6250 | 29 | 500 | 0.1379 | 0.0110 | 0.0423 | 0.1351 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
