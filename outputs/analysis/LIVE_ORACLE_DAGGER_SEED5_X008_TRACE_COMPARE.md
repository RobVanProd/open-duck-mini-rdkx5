# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[5]`
trace_seeds: `[5]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `iter0` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0458 | 0.5724 | 0.0978 | 0.1462 | 3.6534 | 0.2612 |
| `iter1` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 74 | `fall_or_nan` | -0.2043 | -2.5536 | 0.0905 | 0.0674 | 3.2508 | 0.2666 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter0` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.5724 | 0.0458 | 0.0978 | 0.1462 |
| `iter1` | 1 | 1 | 0 | 74.0000 | 74 | 74 | -2.5536 | -0.2043 | 0.0905 | 0.0674 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
