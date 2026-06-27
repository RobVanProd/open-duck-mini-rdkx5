# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[0, 5]`
trace_seeds: `[0, 5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `best` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0365 | 0.4560 | 0.1188 | 0.1520 | 2.1043 | 0.1985 |
| `best` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0362 | 0.4527 | 0.1151 | 0.1462 | 2.1381 | 0.1926 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `best` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4544 | 0.0363 | 0.1169 | 0.1491 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
