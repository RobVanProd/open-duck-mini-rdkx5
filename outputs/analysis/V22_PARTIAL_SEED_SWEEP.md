# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.04`
bridge_mode: `vanilla`
reward_overrides_json: `outputs/analysis/staged_curriculum_training_plan_v22.json`
reward_overrides_phase: `phase1_strong_step_prior_lock_probe`
duration_s: `15.0`
seeds: `[0, 1, 2, 3]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `v22_partial_61440` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0018 | -0.0450 | 0.0160 | 0.1537 | 0.3184 | 0.0667 |
| `v22_partial_61440` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.0895 | -2.2364 | 0.0082 | 0.1000 | 0.4035 | 0.2241 |
| `v22_partial_61440` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | 0.0036 | 0.0889 | 0.0059 | 0.1526 | 0.3639 | 0.0913 |
| `v22_partial_61440` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0182 | -0.4547 | 0.0691 | 0.1588 | 0.5528 | 0.1026 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `v22_partial_61440` | 4 | 4 | 0 | 60.7500 | 33 | 70 | -0.6618 | -0.0265 | 0.0248 | 0.1413 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
