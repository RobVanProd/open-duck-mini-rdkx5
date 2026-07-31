# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `scale_0p75` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0005 | 0.0061 | 0.0237 | 0.1520 | 0.4454 | 0.0722 |
| `scale_0p75` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | -0.0011 | -0.0135 | 0.0233 | 0.1556 | 0.4204 | 0.0711 |
| `scale_0p75` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0016 | 0.0203 | 0.0210 | 0.1509 | 0.3939 | 0.0707 |
| `scale_0p75` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | -0.0055 | -0.0693 | 0.0321 | 0.1549 | 0.3839 | 0.0697 |
| `scale_0p75` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0031 | 0.0392 | 0.0207 | 0.1506 | 0.3937 | 0.0708 |
| `scale_0p75` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0053 | 0.0659 | 0.0201 | 0.1463 | 0.5414 | 0.0734 |
| `scale_0p75` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | -0.0015 | -0.0193 | 0.0212 | 0.1558 | 0.4577 | 0.0740 |
| `scale_0p75` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 500 | `duration_complete` | 0.0006 | 0.0071 | 0.0215 | 0.1559 | 0.4004 | 0.0703 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `scale_0p75` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.0046 | 0.0004 | 0.0230 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
