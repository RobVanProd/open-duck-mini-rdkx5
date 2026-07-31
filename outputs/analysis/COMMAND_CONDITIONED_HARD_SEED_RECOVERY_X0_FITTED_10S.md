# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
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
| `command_conditioned_hard_seed_recovery_candidate` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0003 | NA | 0.0239 | 0.1520 | 0.4578 | 0.0754 |
| `command_conditioned_hard_seed_recovery_candidate` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0013 | NA | 0.0239 | 0.1556 | 0.4676 | 0.0744 |
| `command_conditioned_hard_seed_recovery_candidate` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0016 | NA | 0.0216 | 0.1509 | 0.4287 | 0.0732 |
| `command_conditioned_hard_seed_recovery_candidate` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0056 | NA | 0.0331 | 0.1548 | 0.4289 | 0.0724 |
| `command_conditioned_hard_seed_recovery_candidate` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0214 | 0.1506 | 0.4411 | 0.0748 |
| `command_conditioned_hard_seed_recovery_candidate` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 73 | `fall_or_nan` | -0.2176 | NA | 0.0999 | 0.0464 | 1.2246 | 0.1633 |
| `command_conditioned_hard_seed_recovery_candidate` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0011 | NA | 0.0216 | 0.1557 | 0.4704 | 0.0752 |
| `command_conditioned_hard_seed_recovery_candidate` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0005 | NA | 0.0237 | 0.1559 | 0.4377 | 0.0737 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_candidate` | 8 | 1 | 7 | 446.6250 | 73 | 500 | NA | -0.0275 | 0.0336 | 0.1402 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
