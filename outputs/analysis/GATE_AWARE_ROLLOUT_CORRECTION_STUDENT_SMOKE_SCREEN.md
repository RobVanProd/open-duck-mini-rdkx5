# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[1, 4]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `gate_aware_rollout_correction_student_smoke` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 98 | `fall_or_nan` | 0.1949 | 2.4359 | 1.0659 | -0.0125 | 5.2400 | 0.3140 |
| `gate_aware_rollout_correction_student_smoke` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | `fall_or_nan` | -0.2444 | -3.0548 | 0.0304 | 0.0987 | 5.2400 | 0.3174 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gate_aware_rollout_correction_student_smoke` | 2 | 2 | 0 | 77.0000 | 56 | 98 | -0.3094 | -0.0248 | 0.5482 | 0.0431 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
