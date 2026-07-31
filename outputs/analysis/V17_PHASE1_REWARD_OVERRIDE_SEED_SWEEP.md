# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
bridge_mode: `vanilla`
reward_overrides_json: `outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T141427Z/downloaded/open_duck_colab_cli_staged-curriculum_20260624T141521Z/open_duck_mini_staged_curriculum_cli_20260624T141603Z_staged_curriculum_plan.json`
reward_overrides_phase: `phase1_hard_signed_progress_discovery`
duration_s: `5.0`
seeds: `[0, 1, 2, 3]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `v17_phase1` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | 0.0111 | 0.1391 | 0.1681 | 0.1536 | 0.5901 | 0.1169 |
| `v17_phase1` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | -0.0996 | -1.2447 | 0.0006 | 0.1026 | 0.6897 | 0.1797 |
| `v17_phase1` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | 0.0182 | 0.2281 | 0.1274 | 0.1525 | 0.4908 | 0.1320 |
| `v17_phase1` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | -0.0055 | -0.0692 | 0.1465 | 0.1561 | 0.5666 | 0.0969 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v17_phase1` | 4 | 4 | 0 | 53.0000 | 32 | 60 | -0.2367 | -0.0189 | 0.1106 | 0.1412 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
