# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `a2_164k` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0004 | NA | 0.0254 | 0.1520 | 0.4995 | 0.0000 | 0.0749 |
| `a2_164k` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0001 | NA | 0.0255 | 0.1556 | 0.6209 | 0.0000 | 0.0751 |
| `a2_164k` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0011 | NA | 0.0255 | 0.1509 | 0.4985 | 0.0000 | 0.0750 |
| `a2_164k` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0035 | NA | 0.0264 | 0.1549 | 0.4970 | 0.0000 | 0.0730 |
| `a2_164k` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0022 | NA | 0.0253 | 0.1506 | 0.4989 | 0.0000 | 0.0750 |
| `a2_164k` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0036 | NA | 0.0254 | 0.1462 | 0.4996 | 0.0000 | 0.0751 |
| `a2_164k` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0008 | NA | 0.0254 | 0.1557 | 0.4974 | 0.0000 | 0.0747 |
| `a2_164k` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0004 | NA | 0.0273 | 0.1559 | 0.4989 | 0.0000 | 0.0751 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `a2_164k` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0004 | 0.0258 | 0.1527 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
