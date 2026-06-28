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
| `stage_a` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0269 | 0.1520 | 0.2193 | 0.0000 | 0.0593 |
| `stage_a` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0005 | NA | 0.0266 | 0.1556 | 0.2193 | 0.0000 | 0.0593 |
| `stage_a` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0011 | NA | 0.0269 | 0.1509 | 0.2185 | 0.0000 | 0.0592 |
| `stage_a` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0034 | NA | 0.0274 | 0.1544 | 0.2190 | 0.0000 | 0.0592 |
| `stage_a` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0023 | NA | 0.0267 | 0.1506 | 0.2201 | 0.0000 | 0.0594 |
| `stage_a` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0037 | NA | 0.0270 | 0.1462 | 0.2208 | 0.0000 | 0.0593 |
| `stage_a` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0008 | NA | 0.0267 | 0.1557 | 0.2194 | 0.0000 | 0.0594 |
| `stage_a` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0265 | 0.1559 | 0.2193 | 0.0000 | 0.0593 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0004 | 0.0268 | 0.1527 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
