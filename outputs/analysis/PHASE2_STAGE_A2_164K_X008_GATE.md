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

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `a2_164k` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0295 | 0.3688 | 0.1095 | 0.1520 | 1.7953 | 0.0000 | 0.2004 |
| `a2_164k` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0294 | 0.3670 | 0.1104 | 0.1556 | 1.7950 | 0.0000 | 0.1992 |
| `a2_164k` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0318 | 0.3969 | 0.1111 | 0.1509 | 1.8055 | 0.0000 | 0.1961 |
| `a2_164k` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0251 | 0.3139 | 0.1128 | 0.1557 | 1.7844 | 0.0000 | 0.1975 |
| `a2_164k` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0322 | 0.4020 | 0.1106 | 0.1506 | 1.7839 | 0.0000 | 0.1958 |
| `a2_164k` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3827 | 0.1083 | 0.1462 | 1.7871 | 0.0000 | 0.1953 |
| `a2_164k` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0274 | 0.3427 | 0.1089 | 0.1557 | 1.8015 | 0.0000 | 0.1985 |
| `a2_164k` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0305 | 0.3813 | 0.1095 | 0.1559 | 1.7816 | 0.0000 | 0.1977 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `a2_164k` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3694 | 0.0296 | 0.1101 | 0.1528 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
