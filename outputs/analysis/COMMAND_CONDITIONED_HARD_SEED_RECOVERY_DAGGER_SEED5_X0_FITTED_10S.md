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
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0005 | NA | 0.0194 | 0.1520 | 0.4311 | 0.0721 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0010 | NA | 0.0203 | 0.1556 | 0.4165 | 0.0710 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0018 | NA | 0.0192 | 0.1509 | 0.4051 | 0.0718 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0056 | NA | 0.0292 | 0.1548 | 0.4120 | 0.0703 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0187 | 0.1506 | 0.3949 | 0.0717 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 5 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0053 | NA | 0.0188 | 0.1462 | 0.6016 | 0.0763 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0014 | NA | 0.0200 | 0.1557 | 0.4278 | 0.0729 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0007 | NA | 0.0197 | 0.1559 | 0.4022 | 0.0719 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate` | 8 | 0 | 8 | 500.0000 | 500 | 500 | NA | 0.0004 | 0.0207 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
