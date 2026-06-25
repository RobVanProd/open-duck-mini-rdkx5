# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.04`
bridge_mode: `vanilla`
reward_overrides_json: `outputs/analysis/colab_cli/open-duck-a100-v20-staged-curriculum-20260625T032259Z/manual_partial/open_duck_staged_curriculum_cli/01_phase1_interpolated_reference_seed_x004/phase_01_seed_gate_xp0p040/phase_reward_overrides.json`
reward_overrides_phase: `phase1_interpolated_reference_seed_x004`
duration_s: `5.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `v20` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | 0.0014 | 0.0341 | 0.0759 | 0.1536 | 0.3827 | 0.0710 |
| `v20` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.0913 | -2.2813 | 0.0070 | 0.0916 | 0.5311 | 0.1960 |
| `v20` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | 0.0077 | 0.1926 | 0.0319 | 0.1526 | 0.5577 | 0.0826 |
| `v20` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0157 | -0.3930 | 0.0822 | 0.1579 | 0.4650 | 0.1023 |
| `v20` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 152 | `fall_or_nan` | 0.0080 | 0.1992 | 0.0421 | 0.1513 | 0.1445 | 0.0478 |
| `v20` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 50 | `fall_or_nan` | -0.3133 | -7.8315 | 0.0614 | 0.0506 | 0.7708 | 0.1604 |
| `v20` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0143 | -0.3563 | 0.0296 | 0.1588 | 0.5218 | 0.0993 |
| `v20` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.0135 | -0.3385 | 0.0393 | 0.0961 | 0.7224 | 0.4262 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v20` | 8 | 8 | 0 | 68.6250 | 33 | 152 | -1.3468 | -0.0539 | 0.0462 | 0.1266 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
