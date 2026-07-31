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
trace_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `zero_action_standstill` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0003 | NA | 0.0005 | 0.1521 | 0.0000 | 0.0301 |
| `zero_action_standstill` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0023 | NA | 0.0028 | 0.1557 | 0.0000 | 0.0293 |
| `zero_action_standstill` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0003 | NA | 0.0030 | 0.1511 | 0.0000 | 0.0316 |
| `zero_action_standstill` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 63 | `fall_or_nan` | -0.3415 | NA | 0.2155 | 0.0372 | 0.0000 | 0.0958 |
| `zero_action_standstill` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0023 | NA | 0.0238 | 0.1507 | 0.0000 | 0.0341 |
| `zero_action_standstill` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3322 | NA | 0.0618 | 0.0420 | 0.0000 | 0.2006 |
| `zero_action_standstill` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0020 | NA | 0.0232 | 0.1562 | 0.0000 | 0.0351 |
| `zero_action_standstill` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0008 | NA | 0.0008 | 0.1559 | 0.0000 | 0.0292 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `zero_action_standstill` | 8 | 2 | 6 | 388.8750 | 48 | 500 | NA | -0.0846 | 0.0414 | 0.1251 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
