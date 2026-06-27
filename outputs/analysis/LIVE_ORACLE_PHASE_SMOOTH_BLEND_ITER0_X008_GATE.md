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
| `live_oracle_phase_smooth_blend_iter0_x008` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0329 | 0.4110 | 0.1035 | 0.1520 | 4.4161 | 0.2683 |
| `live_oracle_phase_smooth_blend_iter0_x008` | 1 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0391 | 0.4894 | 0.1059 | 0.1542 | 4.3612 | 0.2676 |
| `live_oracle_phase_smooth_blend_iter0_x008` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0336 | 0.4201 | 0.1074 | 0.1510 | 4.4179 | 0.2697 |
| `live_oracle_phase_smooth_blend_iter0_x008` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0326 | 0.4074 | 0.1088 | 0.1502 | 4.4742 | 0.2704 |
| `live_oracle_phase_smooth_blend_iter0_x008` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0385 | 0.4809 | 0.1071 | 0.1506 | 4.3464 | 0.2679 |
| `live_oracle_phase_smooth_blend_iter0_x008` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0422 | 0.5274 | 0.1053 | 0.1464 | 4.3622 | 0.2708 |
| `live_oracle_phase_smooth_blend_iter0_x008` | 6 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0367 | 0.4582 | 0.1053 | 0.1543 | 4.2557 | 0.2673 |
| `live_oracle_phase_smooth_blend_iter0_x008` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0366 | 0.4571 | 0.1053 | 0.1548 | 4.4125 | 0.2659 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_phase_smooth_blend_iter0_x008` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4564 | 0.0365 | 0.1061 | 0.1517 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
