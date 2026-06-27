# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[3]`
trace_seeds: `[3]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `baseline` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0293 | 0.3661 | 0.1209 | 0.1554 | 2.1254 | 0.1998 |
| `behavior_smoke` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 74 | `fall_or_nan` | -0.2708 | -3.3845 | 0.2264 | 0.0684 | 1.4815 | 0.1446 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.3661 | 0.0293 | 0.1209 | 0.1554 |
| `behavior_smoke` | 1 | 1 | 0 | 74.0000 | 74 | 74 | -3.3845 | -0.2708 | 0.2264 | 0.0684 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
