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
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0365 | 0.4560 | 0.1188 | 0.1520 | 2.1043 | 0.1985 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0357 | 0.4463 | 0.1116 | 0.1556 | 2.1153 | 0.1908 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0360 | 0.4497 | 0.1161 | 0.1509 | 2.1334 | 0.1944 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0250 | 0.3120 | 0.1172 | 0.1554 | 2.1495 | 0.1924 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0359 | 0.4491 | 0.1110 | 0.1506 | 2.1639 | 0.1881 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0362 | 0.4527 | 0.1151 | 0.1462 | 2.1381 | 0.1926 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0321 | 0.4017 | 0.1129 | 0.1557 | 2.1092 | 0.1887 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0374 | 0.4677 | 0.1149 | 0.1559 | 2.1202 | 0.1875 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4294 | 0.0344 | 0.1147 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
