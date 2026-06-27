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
| `recurrent` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 124 | `fall_or_nan` | 0.1343 | 1.6785 | 1.0270 | 0.0134 | 5.2400 | 0.2165 |
| `recurrent` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 97 | `fall_or_nan` | -0.1799 | -2.2485 | 0.2089 | 0.0540 | 5.2400 | 0.2423 |
| `recurrent` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 174 | `fall_or_nan` | 0.0961 | 1.2013 | 0.7936 | 0.0259 | 5.2400 | 0.2816 |
| `recurrent` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 83 | `fall_or_nan` | -0.2523 | -3.1534 | 0.2544 | 0.0635 | 5.2400 | 0.2411 |
| `recurrent` | 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 73 | `fall_or_nan` | -0.2026 | -2.5325 | 0.0029 | 0.0657 | 5.2400 | 0.2614 |
| `recurrent` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 103 | `fall_or_nan` | -0.1634 | -2.0428 | 0.1206 | 0.0465 | 5.2400 | 0.2465 |
| `recurrent` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 153 | `fall_or_nan` | -0.1189 | -1.4861 | 0.1590 | 0.0724 | 5.2400 | 0.2208 |
| `recurrent` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 211 | `fall_or_nan` | 0.0890 | 1.1119 | 0.7683 | 0.0095 | 5.2400 | 0.2516 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `recurrent` | 8 | 8 | 0 | 127.2500 | 73 | 211 | -0.9339 | -0.0747 | 0.4168 | 0.0439 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
