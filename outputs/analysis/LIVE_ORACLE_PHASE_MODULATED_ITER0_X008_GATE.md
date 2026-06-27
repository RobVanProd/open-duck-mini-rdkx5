# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
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

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `live_oracle_phase_modulated_iter0_x008` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0456 | 0.5702 | 0.1050 | 0.1520 | 3.7962 | 0.2628 |
| `live_oracle_phase_modulated_iter0_x008` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0407 | 0.5085 | 0.1044 | 0.1556 | 3.8131 | 0.2600 |
| `live_oracle_phase_modulated_iter0_x008` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0457 | 0.5715 | 0.1072 | 0.1509 | 3.7882 | 0.2591 |
| `live_oracle_phase_modulated_iter0_x008` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0389 | 0.4867 | 0.1155 | 0.1544 | 3.7528 | 0.2621 |
| `live_oracle_phase_modulated_iter0_x008` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0435 | 0.5437 | 0.1067 | 0.1506 | 3.7833 | 0.2591 |
| `live_oracle_phase_modulated_iter0_x008` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.2075 | -2.5932 | 0.0826 | 0.0726 | 3.1976 | 0.2969 |
| `live_oracle_phase_modulated_iter0_x008` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0394 | 0.4928 | 0.1091 | 0.1557 | 3.7649 | 0.2601 |
| `live_oracle_phase_modulated_iter0_x008` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0424 | 0.5298 | 0.1053 | 0.1559 | 3.8548 | 0.2600 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_phase_modulated_iter0_x008` | 8 | 1 | 7 | 665.0000 | 70 | 750 | 0.1388 | 0.0111 | 0.1045 | 0.1435 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
