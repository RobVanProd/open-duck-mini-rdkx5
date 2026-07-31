# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[1, 3, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `hard_seed_recovery_prior` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0341 | 0.4266 | 0.1173 | 0.1556 | 2.0418 | 0.1950 |
| `hard_seed_recovery_prior` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0251 | 0.3140 | 0.1203 | 0.1554 | 2.0015 | 0.1971 |
| `hard_seed_recovery_prior` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0348 | 0.4352 | 0.1172 | 0.1559 | 2.0504 | 0.1926 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `hard_seed_recovery_prior` | 3 | 0 | 3 | 750.0000 | 750 | 750 | 0.3919 | 0.0314 | 0.1183 | 0.1556 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
