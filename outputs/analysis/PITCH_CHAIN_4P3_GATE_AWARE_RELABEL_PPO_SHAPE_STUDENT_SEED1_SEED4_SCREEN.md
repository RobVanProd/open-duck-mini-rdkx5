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
| `gate_aware_relabel_student` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0372 | 0.4652 | 0.0897 | 0.1556 | 3.7264 | 0.2548 |
| `gate_aware_relabel_student` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0380 | 0.4747 | 0.0990 | 0.1506 | 3.6821 | 0.2536 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gate_aware_relabel_student` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4700 | 0.0376 | 0.0943 | 0.1531 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
