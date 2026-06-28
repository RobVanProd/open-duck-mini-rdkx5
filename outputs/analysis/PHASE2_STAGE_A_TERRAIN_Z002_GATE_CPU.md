# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0311 | 0.3892 | 0.1360 | 0.1519 | 1.7871 | 0.0000 | 0.1965 | 0 | NA |
| `stage_a` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0323 | 0.4035 | 0.1395 | 0.1562 | 1.7965 | 0.0000 | 0.1990 | 0 | NA |
| `stage_a` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0328 | 0.4101 | 0.1390 | 0.1511 | 1.8058 | 0.0000 | 0.1998 | 0 | NA |
| `stage_a` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3830 | 0.1374 | 0.1552 | 1.7863 | 0.0000 | 0.1966 | 0 | NA |
| `stage_a` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0325 | 0.4057 | 0.1342 | 0.1506 | 1.7864 | 0.0000 | 0.1988 | 0 | NA |
| `stage_a` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0335 | 0.4192 | 0.1384 | 0.1462 | 1.7694 | 0.0000 | 0.1988 | 0 | NA |
| `stage_a` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0327 | 0.4093 | 0.1378 | 0.1530 | 1.8067 | 0.0000 | 0.1974 | 0 | NA |
| `stage_a` | 7 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0325 | 0.4063 | 0.1361 | 0.1564 | 1.8007 | 0.0000 | 0.2001 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4033 | 0.0323 | 0.1373 | 0.1526 | 0.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
