# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0277 | 0.3464 | 0.1088 | 0.1520 | 1.7415 | 0.0000 | 0.1983 |
| `gain098` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0262 | 0.3281 | 0.1114 | 0.1520 | 1.7589 | 0.0000 | 0.1944 |
| `gain097` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0251 | 0.3142 | 0.1101 | 0.1520 | 1.7139 | 0.0000 | 0.1948 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gain099` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.3464 | 0.0277 | 0.1088 | 0.1520 | 0.0000 |
| `gain098` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.3281 | 0.0262 | 0.1114 | 0.1520 | 0.0000 |
| `gain097` | 1 | 0 | 1 | 750.0000 | 750 | 750 | 0.3142 | 0.0251 | 0.1101 | 0.1520 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
