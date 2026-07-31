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
eval_push_magnitude: `0.1`-`0.2`
push_recovery_window_s: `0.5`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3508 | 0.1213 | 0.1520 | 1.7796 | 0.0000 | 0.1930 | 12 | 0.9167 |
| `stage_a` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3512 | 0.1259 | 0.1556 | 1.7764 | 0.0000 | 0.1961 | 13 | 1.0000 |
| `stage_a` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3562 | 0.1183 | 0.1509 | 1.7845 | 0.0000 | 0.1964 | 13 | 0.9231 |
| `stage_a` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0228 | 0.2845 | 0.1515 | 0.1551 | 1.7700 | 0.0000 | 0.1893 | 13 | 1.0000 |
| `stage_a` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0315 | 0.3933 | 0.1141 | 0.1506 | 1.7542 | 0.0000 | 0.1950 | 12 | 1.0000 |
| `stage_a` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0291 | 0.3642 | 0.1180 | 0.1462 | 1.7529 | 0.0000 | 0.1947 | 13 | 1.0000 |
| `stage_a` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0266 | 0.3330 | 0.1378 | 0.1557 | 1.7732 | 0.0000 | 0.1953 | 13 | 0.9231 |
| `stage_a` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0272 | 0.3404 | 0.1200 | 0.1557 | 1.7845 | 0.0000 | 0.1964 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3467 | 0.0277 | 0.1259 | 0.1527 | 0.0000 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
