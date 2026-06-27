# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `flat_terrain`
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
| `support_transition_smoke` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0004 | NA | 0.0074 | 0.1536 | 0.2667 | 0.0637 |
| `support_transition_smoke` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | -0.0261 | NA | 0.0015 | 0.0817 | 1.1102 | 0.2729 |
| `support_transition_smoke` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | NA | 0.0074 | 0.1525 | 0.2664 | 0.0634 |
| `support_transition_smoke` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0020 | NA | 0.0074 | 0.1588 | 0.2664 | 0.0633 |
| `support_transition_smoke` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0020 | NA | 0.0074 | 0.1515 | 0.2695 | 0.0637 |
| `support_transition_smoke` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0033 | NA | 0.0074 | 0.1467 | 0.2665 | 0.0637 |
| `support_transition_smoke` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0011 | NA | 0.0074 | 0.1587 | 0.2665 | 0.0636 |
| `support_transition_smoke` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0040 | NA | 0.0278 | 0.0827 | 0.8423 | 0.3268 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `support_transition_smoke` | 8 | 2 | 6 | 570.6250 | 32 | 750 | NA | -0.0023 | 0.0092 | 0.1358 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
