# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[0, 3]`
trace_seeds: `[0, 3]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_candidate` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0003 | NA | 0.0239 | 0.1520 | 0.4578 | 0.0754 |
| `command_conditioned_hard_seed_recovery_candidate` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0056 | NA | 0.0331 | 0.1548 | 0.4289 | 0.0724 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_candidate` | 2 | 0 | 2 | 500.0000 | 500 | 500 | NA | -0.0027 | 0.0285 | 0.1534 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
