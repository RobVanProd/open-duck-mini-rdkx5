# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `hard_seed_recovery_prior` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0284 | NA | 0.1170 | 0.1521 | 2.0335 | 0.1951 |
| `hard_seed_recovery_prior` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0324 | NA | 0.1164 | 0.1556 | 2.0677 | 0.1920 |
| `hard_seed_recovery_prior` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0147 | NA | 0.1080 | 0.1509 | 1.8701 | 0.1763 |
| `hard_seed_recovery_prior` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0147 | NA | 0.1139 | 0.1554 | 1.8985 | 0.1778 |
| `hard_seed_recovery_prior` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0283 | NA | 0.1147 | 0.1506 | 1.9963 | 0.1827 |
| `hard_seed_recovery_prior` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0341 | NA | 0.1192 | 0.1456 | 2.0192 | 0.1969 |
| `hard_seed_recovery_prior` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0090 | NA | 0.1068 | 0.1558 | 1.7983 | 0.1648 |
| `hard_seed_recovery_prior` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0337 | NA | 0.1156 | 0.1559 | 2.0411 | 0.1919 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `hard_seed_recovery_prior` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0244 | 0.1139 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
