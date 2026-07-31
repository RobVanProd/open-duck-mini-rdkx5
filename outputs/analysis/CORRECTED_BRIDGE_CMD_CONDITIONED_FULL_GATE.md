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
| `cmd_conditioned` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0363 | 0.4535 | 0.1225 | 0.1520 | 1.7364 | 0.0000 | 0.1943 |
| `cmd_conditioned` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0352 | 0.4404 | 0.1182 | 0.1556 | 1.7348 | 0.0000 | 0.1921 |
| `cmd_conditioned` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0369 | 0.4618 | 0.1211 | 0.1509 | 1.7271 | 0.0000 | 0.1956 |
| `cmd_conditioned` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0296 | 0.3697 | 0.1235 | 0.1551 | 1.7277 | 0.0000 | 0.1973 |
| `cmd_conditioned` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0308 | 0.3855 | 0.1156 | 0.1506 | 1.7381 | 0.0000 | 0.1879 |
| `cmd_conditioned` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0366 | 0.4572 | 0.1244 | 0.1462 | 1.7472 | 0.0000 | 0.1970 |
| `cmd_conditioned` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3827 | 0.1197 | 0.1554 | 1.7422 | 0.0000 | 0.1884 |
| `cmd_conditioned` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0352 | 0.4395 | 0.1171 | 0.1559 | 1.7315 | 0.0000 | 0.1914 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmd_conditioned` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4238 | 0.0339 | 0.1203 | 0.1527 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
