# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.04`
bridge_mode: `vanilla`
reward_overrides_json: `outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T141427Z/downloaded/open_duck_colab_cli_staged-curriculum_20260624T141521Z/open_duck_mini_staged_curriculum_cli_20260624T141603Z_staged_curriculum_plan.json`
reward_overrides_phase: `phase1_hard_signed_progress_discovery`
duration_s: `5.0`
seeds: `[0, 1, 2, 3]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `v17_phase1` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | -0.0026 | -0.0652 | 0.0826 | 0.1535 | 0.4985 | 0.1025 |
| `v17_phase1` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | -0.0949 | -2.3730 | 0.0073 | 0.0961 | 0.6515 | 0.2020 |
| `v17_phase1` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | 0.0078 | 0.1945 | 0.0261 | 0.1526 | 0.9218 | 0.0992 |
| `v17_phase1` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 60 | `fall_or_nan` | -0.0208 | -0.5206 | 0.0766 | 0.1586 | 0.8051 | 0.1119 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v17_phase1` | 4 | 4 | 0 | 53.7500 | 35 | 60 | -0.6911 | -0.0276 | 0.0482 | 0.1402 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
