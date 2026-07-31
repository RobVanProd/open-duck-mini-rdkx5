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
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0006 | NA | 0.0209 | 0.1520 | 0.5036 | 0.0742 |
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0014 | NA | 0.0229 | 0.1556 | 0.4604 | 0.0716 |
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0017 | NA | 0.0214 | 0.1509 | 0.4063 | 0.0706 |
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0056 | NA | 0.0285 | 0.1550 | 0.4067 | 0.0697 |
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0210 | 0.1506 | 0.4127 | 0.0710 |
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.2567 | NA | 0.0626 | 0.0680 | 1.5884 | 0.1956 |
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0014 | NA | 0.0206 | 0.1557 | 0.4189 | 0.0710 |
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0004 | NA | 0.0228 | 0.1559 | 0.4138 | 0.0708 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_hard_seed_recovery_weighted_seed5_x0_candidate` | 8 | 1 | 7 | 444.6250 | 57 | 500 | NA | -0.0324 | 0.0276 | 0.1430 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
