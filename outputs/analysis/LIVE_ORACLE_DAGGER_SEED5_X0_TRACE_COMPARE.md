# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
| `iter0` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0434 | NA | 0.0963 | 0.1462 | 3.7090 | 0.2678 |
| `iter1` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3358 | NA | 0.0628 | 0.0421 | 1.5031 | 0.2330 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter0` | 1 | 0 | 1 | 750.0000 | 750 | 750 | NA | 0.0434 | 0.0963 | 0.1462 |
| `iter1` | 1 | 1 | 0 | 48.0000 | 48 | 48 | NA | -0.3358 | 0.0628 | 0.0421 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
