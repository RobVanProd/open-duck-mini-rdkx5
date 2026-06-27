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
| `support_transition_smoke_backlash` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0015 | 0.0183 | 0.0514 | 0.1520 | 1.1220 | 0.1033 |
| `support_transition_smoke_backlash` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | -0.0014 | -0.0172 | 0.0038 | 0.1556 | 0.5239 | 0.0614 |
| `support_transition_smoke_backlash` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0007 | 0.0082 | 0.0038 | 0.1509 | 0.5110 | 0.0604 |
| `support_transition_smoke_backlash` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 78 | `fall_or_nan` | -0.2514 | -3.1430 | 0.2257 | 0.0781 | 1.7997 | 0.1442 |
| `support_transition_smoke_backlash` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0020 | 0.0256 | 0.0077 | 0.1506 | 0.7247 | 0.0769 |
| `support_transition_smoke_backlash` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0032 | 0.0401 | 0.0353 | 0.1459 | 0.8870 | 0.0944 |
| `support_transition_smoke_backlash` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0182 | 0.2277 | 0.1045 | 0.1557 | 2.0856 | 0.1669 |
| `support_transition_smoke_backlash` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0001 | 0.0009 | 0.0041 | 0.1559 | 0.4921 | 0.0602 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `support_transition_smoke_backlash` | 8 | 1 | 7 | 666.0000 | 78 | 750 | -0.3549 | -0.0284 | 0.0545 | 0.1431 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
