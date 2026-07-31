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
| `cmd_pitch_rl_2p25_step0` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0003 | NA | 0.0233 | 0.1520 | 0.4125 | 0.0720 |
| `cmd_pitch_rl_2p25_step0` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | -0.0006 | NA | 0.0238 | 0.1556 | 0.7493 | 0.0861 |
| `cmd_pitch_rl_2p25_step0` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0018 | NA | 0.0241 | 0.1509 | 0.4198 | 0.0715 |
| `cmd_pitch_rl_2p25_step0` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0054 | NA | 0.0336 | 0.1550 | 0.4071 | 0.0711 |
| `cmd_pitch_rl_2p25_step0` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0218 | 0.1506 | 0.3877 | 0.0713 |
| `cmd_pitch_rl_2p25_step0` | 5 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0054 | NA | 0.0232 | 0.1463 | 0.5053 | 0.0728 |
| `cmd_pitch_rl_2p25_step0` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0014 | NA | 0.0239 | 0.1557 | 0.4910 | 0.0751 |
| `cmd_pitch_rl_2p25_step0` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0004 | NA | 0.0225 | 0.1559 | 0.3974 | 0.0710 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_pitch_rl_2p25_step0` | 8 | 0 | 8 | 500.0000 | 500 | 500 | NA | 0.0005 | 0.0245 | 0.1528 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
