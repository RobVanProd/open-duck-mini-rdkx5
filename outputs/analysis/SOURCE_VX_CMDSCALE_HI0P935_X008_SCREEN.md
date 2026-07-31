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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `cmdscale_hi0p935` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0307 | 0.3841 | 0.0938 | 0.1520 | 3.5196 | 0.2504 |
| `cmdscale_hi0p935` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0336 | 0.4203 | 0.0919 | 0.1463 | 3.4909 | 0.2503 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmdscale_hi0p935` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4022 | 0.0322 | 0.0929 | 0.1491 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
