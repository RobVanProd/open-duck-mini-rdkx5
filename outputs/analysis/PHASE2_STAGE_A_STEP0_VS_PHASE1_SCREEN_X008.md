# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `step0` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0354 | 0.4419 | 0.1175 | 0.1520 | 1.7305 | 0.0000 | 0.1938 |
| `phase1` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0338 | 0.4229 | 0.1204 | 0.1520 | 1.7427 | 0.0000 | 0.1961 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `step0` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.4419 | 0.0354 | 0.1175 | 0.1520 | 0.0000 |
| `phase1` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.4229 | 0.0338 | 0.1204 | 0.1520 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
