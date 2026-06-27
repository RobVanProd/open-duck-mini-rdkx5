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

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `live_oracle_dagger_iter1` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0265 | 0.1521 | 0.1161 | 0.0416 |
| `live_oracle_dagger_iter1` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0012 | NA | 0.0313 | 0.1557 | 0.1309 | 0.0416 |
| `live_oracle_dagger_iter1` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0273 | 0.1511 | 0.1160 | 0.0416 |
| `live_oracle_dagger_iter1` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0041 | NA | 0.0279 | 0.1528 | 0.1853 | 0.0416 |
| `live_oracle_dagger_iter1` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0015 | NA | 0.0254 | 0.1507 | 0.1159 | 0.0416 |
| `live_oracle_dagger_iter1` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | `fall_or_nan` | -0.3358 | NA | 0.0628 | 0.0421 | 1.5031 | 0.2330 |
| `live_oracle_dagger_iter1` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0012 | NA | 0.0352 | 0.1562 | 0.1251 | 0.0416 |
| `live_oracle_dagger_iter1` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0004 | NA | 0.0290 | 0.1559 | 0.1671 | 0.0416 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `live_oracle_dagger_iter1` | 8 | 1 | 7 | 662.2500 | 48 | 750 | NA | -0.0425 | 0.0332 | 0.1396 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
