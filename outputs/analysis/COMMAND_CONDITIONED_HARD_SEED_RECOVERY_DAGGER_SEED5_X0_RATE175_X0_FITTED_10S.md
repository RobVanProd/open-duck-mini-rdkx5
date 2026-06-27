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
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0007 | NA | 0.0208 | 0.1520 | 0.4631 | 0.0752 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0010 | NA | 0.0211 | 0.1556 | 0.4555 | 0.0749 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0013 | NA | 0.0198 | 0.1509 | 0.4356 | 0.0746 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0054 | NA | 0.0291 | 0.1548 | 0.4539 | 0.0736 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0197 | 0.1506 | 0.4552 | 0.0750 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 59 | `fall_or_nan` | -0.2491 | NA | 0.0640 | 0.0639 | 1.3830 | 0.2102 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0017 | NA | 0.0203 | 0.1557 | 0.4597 | 0.0749 |
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0004 | NA | 0.0249 | 0.1559 | 0.4630 | 0.0746 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate` | 8 | 1 | 7 | 444.8750 | 59 | 500 | NA | -0.0314 | 0.0275 | 0.1424 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
