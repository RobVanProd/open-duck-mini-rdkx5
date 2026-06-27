# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `flat_terrain`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `cmd_pitch_step0_flat` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0004 | NA | 0.0025 | 0.1536 | 0.2820 | 0.0634 |
| `cmd_pitch_step0_flat` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 31 | `fall_or_nan` | 0.0076 | NA | 0.0015 | 0.0858 | 1.8460 | 0.2600 |
| `cmd_pitch_step0_flat` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0013 | NA | 0.0027 | 0.1525 | 0.2797 | 0.0634 |
| `cmd_pitch_step0_flat` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0020 | NA | 0.0036 | 0.1595 | 0.2811 | 0.0631 |
| `cmd_pitch_step0_flat` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0020 | NA | 0.0026 | 0.1515 | 0.2823 | 0.0635 |
| `cmd_pitch_step0_flat` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0031 | NA | 0.0026 | 0.1468 | 0.3268 | 0.0636 |
| `cmd_pitch_step0_flat` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0015 | NA | 0.0027 | 0.1587 | 0.2816 | 0.0635 |
| `cmd_pitch_step0_flat` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | 0.0079 | NA | 0.0427 | 0.0714 | 1.4149 | 0.3086 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_pitch_step0_flat` | 8 | 2 | 6 | 570.6250 | 31 | 750 | NA | 0.0023 | 0.0076 | 0.1350 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
