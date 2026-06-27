# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[3, 5]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `scale_0p25` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0059 | NA | 0.0375 | 0.1524 | 0.0544 | 0.0379 |
| `scale_0p25` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3136 | NA | 0.0559 | 0.0575 | 0.1794 | 0.1966 |
| `scale_0p5` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0058 | NA | 0.0307 | 0.1533 | 0.1465 | 0.0487 |
| `scale_0p5` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 52 | `fall_or_nan` | -0.3013 | NA | 0.0542 | 0.0493 | 0.5305 | 0.1933 |
| `scale_0p75` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0056 | NA | 0.0319 | 0.1549 | 0.3839 | 0.0694 |
| `scale_0p75` | 5 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0052 | NA | 0.0205 | 0.1463 | 0.4723 | 0.0729 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `scale_0p25` | 2 | 1 | 1 | 274.0000 | 48 | 500 | NA | -0.1598 | 0.0467 | 0.1049 |
| `scale_0p5` | 2 | 1 | 1 | 276.0000 | 52 | 500 | NA | -0.1535 | 0.0424 | 0.1013 |
| `scale_0p75` | 2 | 0 | 2 | 500.0000 | 500 | 500 | NA | -0.0002 | 0.0262 | 0.1506 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
