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
| `cmdscale_0p75_to_1p0_x008` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0004 | NA | 0.0231 | 0.1520 | 0.3955 | 0.0711 |
| `cmdscale_0p75_to_1p0_x008` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0010 | NA | 0.0248 | 0.1556 | 0.4235 | 0.0708 |
| `cmdscale_0p75_to_1p0_x008` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0016 | NA | 0.0209 | 0.1509 | 0.3806 | 0.0704 |
| `cmdscale_0p75_to_1p0_x008` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0056 | NA | 0.0319 | 0.1549 | 0.3839 | 0.0694 |
| `cmdscale_0p75_to_1p0_x008` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0212 | 0.1506 | 0.3939 | 0.0712 |
| `cmdscale_0p75_to_1p0_x008` | 5 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0052 | NA | 0.0205 | 0.1463 | 0.4723 | 0.0729 |
| `cmdscale_0p75_to_1p0_x008` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0016 | NA | 0.0207 | 0.1557 | 0.4430 | 0.0720 |
| `cmdscale_0p75_to_1p0_x008` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0006 | NA | 0.0223 | 0.1559 | 0.3932 | 0.0704 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmdscale_0p75_to_1p0_x008` | 8 | 0 | 8 | 500.0000 | 500 | 500 | NA | 0.0003 | 0.0232 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
