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
| `command_conditioned_hard_seed_recovery_candidate` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0384 | 0.4799 | 0.1217 | 0.1520 | 2.0483 | 0.1965 |
| `command_conditioned_hard_seed_recovery_candidate` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0355 | 0.4436 | 0.1203 | 0.1556 | 2.0433 | 0.1908 |
| `command_conditioned_hard_seed_recovery_candidate` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0355 | 0.4436 | 0.1237 | 0.1509 | 2.0477 | 0.1986 |
| `command_conditioned_hard_seed_recovery_candidate` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0289 | 0.3610 | 0.1291 | 0.1559 | 2.0949 | 0.1963 |
| `command_conditioned_hard_seed_recovery_candidate` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0343 | 0.4282 | 0.1147 | 0.1506 | 2.0304 | 0.1909 |
| `command_conditioned_hard_seed_recovery_candidate` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0371 | 0.4632 | 0.1236 | 0.1462 | 2.0810 | 0.1984 |
| `command_conditioned_hard_seed_recovery_candidate` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0311 | 0.3890 | 0.1197 | 0.1557 | 2.0573 | 0.1896 |
| `command_conditioned_hard_seed_recovery_candidate` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0364 | 0.4551 | 0.1176 | 0.1559 | 2.0259 | 0.1887 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_candidate` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.4329 | 0.0346 | 0.1213 | 0.1529 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
