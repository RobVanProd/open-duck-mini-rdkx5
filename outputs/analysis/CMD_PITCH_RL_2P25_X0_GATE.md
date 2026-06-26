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
| `cmd_pitch_rl_2p25` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0004 | NA | 0.0232 | 0.1520 | 0.4162 | 0.0716 |
| `cmd_pitch_rl_2p25` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | -0.0006 | NA | 0.0258 | 0.1556 | 0.6479 | 0.0837 |
| `cmd_pitch_rl_2p25` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0018 | NA | 0.0234 | 0.1509 | 0.4186 | 0.0718 |
| `cmd_pitch_rl_2p25` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0054 | NA | 0.0338 | 0.1550 | 0.3972 | 0.0710 |
| `cmd_pitch_rl_2p25` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0229 | 0.1506 | 0.3902 | 0.0718 |
| `cmd_pitch_rl_2p25` | 5 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0054 | NA | 0.0226 | 0.1463 | 0.4979 | 0.0720 |
| `cmd_pitch_rl_2p25` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0015 | NA | 0.0244 | 0.1558 | 0.4018 | 0.0714 |
| `cmd_pitch_rl_2p25` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0004 | NA | 0.0230 | 0.1559 | 0.3887 | 0.0709 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_pitch_rl_2p25` | 8 | 0 | 8 | 500.0000 | 500 | 500 | NA | 0.0004 | 0.0249 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
