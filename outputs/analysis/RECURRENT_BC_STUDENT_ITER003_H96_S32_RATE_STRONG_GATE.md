# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `recurrent_rate` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 50 | `fall_or_nan` | -0.3288 | -4.1098 | 0.0343 | 0.0790 | 5.2400 | 0.2671 |
| `recurrent_rate` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3664 | -4.5803 | 0.1160 | 0.0773 | 5.2400 | 0.2815 |
| `recurrent_rate` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 61 | `fall_or_nan` | -0.2702 | -3.3769 | 0.1133 | 0.0618 | 5.2400 | 0.3342 |
| `recurrent_rate` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | `fall_or_nan` | -0.3933 | -4.9162 | 0.2605 | 0.0420 | 5.2400 | 0.3432 |
| `recurrent_rate` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 43 | `fall_or_nan` | -0.3403 | -4.2533 | 0.0153 | 0.0787 | 5.2400 | 0.2467 |
| `recurrent_rate` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 50 | `fall_or_nan` | -0.3134 | -3.9177 | 0.0539 | 0.0673 | 5.2400 | 0.3280 |
| `recurrent_rate` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 40 | `fall_or_nan` | -0.4473 | -5.5916 | 0.0523 | 0.0370 | 5.2400 | 0.3314 |
| `recurrent_rate` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 50 | `fall_or_nan` | -0.3394 | -4.2420 | 0.0142 | 0.0374 | 5.2400 | 0.2538 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent_rate` | 8 | 8 | 0 | 49.7500 | 40 | 61 | -4.3735 | -0.3499 | 0.0825 | 0.0601 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
