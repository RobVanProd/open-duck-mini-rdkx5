# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.04`
bridge_mode: `vanilla`
reward_overrides_json: `outputs/analysis/v18_a100_staged_plan.json`
reward_overrides_phase: `phase1_x004_dense_progress_discovery`
duration_s: `5.0`
seeds: `[0, 1]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `phase_01` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 50 | `fall_or_nan` | 0.0034 | 0.0845 | 0.0774 | 0.1536 | 0.4275 | 0.1433 |
| `phase_01` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.0954 | -2.3845 | 0.0039 | 0.1009 | 0.7652 | 0.2063 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_01` | 2 | 2 | 0 | 41.5000 | 33 | 50 | -1.1500 | -0.0460 | 0.0407 | 0.1273 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
