# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
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
| `hard_seed_recovery_prior` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0283 | 0.3539 | 0.1181 | 0.1521 | 2.0090 | 0.1920 |
| `hard_seed_recovery_prior` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0341 | 0.4266 | 0.1173 | 0.1556 | 2.0418 | 0.1950 |
| `hard_seed_recovery_prior` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0218 | 0.2731 | 0.1139 | 0.1509 | 1.9642 | 0.1884 |
| `hard_seed_recovery_prior` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0251 | 0.3140 | 0.1203 | 0.1554 | 2.0015 | 0.1971 |
| `hard_seed_recovery_prior` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0099 | 0.1243 | 0.1030 | 0.1506 | 1.7041 | 0.1629 |
| `hard_seed_recovery_prior` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0346 | 0.4328 | 0.1174 | 0.1456 | 2.0288 | 0.1989 |
| `hard_seed_recovery_prior` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0058 | 0.0724 | 0.0945 | 0.1558 | 1.5577 | 0.1512 |
| `hard_seed_recovery_prior` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0348 | 0.4352 | 0.1172 | 0.1559 | 2.0504 | 0.1926 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `hard_seed_recovery_prior` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3040 | 0.0243 | 0.1127 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
