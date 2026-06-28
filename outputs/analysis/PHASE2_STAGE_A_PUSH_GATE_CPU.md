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
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0275 | 0.3433 | 0.1118 | 0.1520 | 1.7565 | 0.0000 | 0.1945 | 12 | 0.9167 |
| `stage_a` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0288 | 0.3605 | 0.1149 | 0.1556 | 1.7633 | 0.0000 | 0.1932 | 13 | 1.0000 |
| `stage_a` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0300 | 0.3750 | 0.1160 | 0.1509 | 1.7649 | 0.0000 | 0.1960 | 13 | 0.9231 |
| `stage_a` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0233 | 0.2911 | 0.1163 | 0.1551 | 1.7741 | 0.0000 | 0.1916 | 13 | 1.0000 |
| `stage_a` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0314 | 0.3925 | 0.1123 | 0.1506 | 1.7564 | 0.0000 | 0.1956 | 12 | 1.0000 |
| `stage_a` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0295 | 0.3687 | 0.1123 | 0.1462 | 1.7529 | 0.0000 | 0.1959 | 13 | 1.0000 |
| `stage_a` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0271 | 0.3385 | 0.1203 | 0.1557 | 1.7722 | 0.0000 | 0.1940 | 13 | 0.9231 |
| `stage_a` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3565 | 0.1179 | 0.1559 | 1.7643 | 0.0000 | 0.1975 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3533 | 0.0283 | 0.1152 | 0.1528 | 0.0000 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
