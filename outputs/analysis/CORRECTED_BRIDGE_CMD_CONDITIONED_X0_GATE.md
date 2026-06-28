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
| `cmd_conditioned` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0006 | NA | 0.0195 | 0.1520 | 0.4603 | 0.0000 | 0.0748 |
| `cmd_conditioned` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0004 | NA | 0.0199 | 0.1556 | 0.4609 | 0.0000 | 0.0746 |
| `cmd_conditioned` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | NA | 0.0196 | 0.1509 | 0.4319 | 0.0000 | 0.0745 |
| `cmd_conditioned` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0036 | NA | 0.0197 | 0.1548 | 0.4550 | 0.0000 | 0.0739 |
| `cmd_conditioned` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0021 | NA | 0.0195 | 0.1506 | 0.4509 | 0.0000 | 0.0747 |
| `cmd_conditioned` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0036 | NA | 0.0193 | 0.1462 | 0.4595 | 0.0000 | 0.0748 |
| `cmd_conditioned` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0010 | NA | 0.0196 | 0.1557 | 0.4560 | 0.0000 | 0.0747 |
| `cmd_conditioned` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0207 | 0.1559 | 0.4564 | 0.0000 | 0.0747 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_conditioned` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0003 | 0.0197 | 0.1527 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
