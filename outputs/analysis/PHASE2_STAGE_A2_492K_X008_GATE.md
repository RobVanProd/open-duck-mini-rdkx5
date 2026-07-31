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
| `a2_492k` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0221 | 0.2766 | 0.0937 | 0.1520 | 1.6106 | 0.0000 | 0.1861 |
| `a2_492k` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0204 | 0.2549 | 0.0912 | 0.1556 | 1.6524 | 0.0000 | 0.1846 |
| `a2_492k` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0220 | 0.2744 | 0.0926 | 0.1509 | 1.6591 | 0.0000 | 0.1901 |
| `a2_492k` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0153 | 0.1915 | 0.0937 | 0.1552 | 1.6350 | 0.0000 | 0.1851 |
| `a2_492k` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0216 | 0.2701 | 0.0928 | 0.1506 | 1.6269 | 0.0000 | 0.1785 |
| `a2_492k` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0230 | 0.2870 | 0.0923 | 0.1462 | 1.6039 | 0.0000 | 0.1886 |
| `a2_492k` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0197 | 0.2459 | 0.0947 | 0.1557 | 1.6224 | 0.0000 | 0.1841 |
| `a2_492k` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0211 | 0.2633 | 0.0911 | 0.1559 | 1.6180 | 0.0000 | 0.1838 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `a2_492k` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.2580 | 0.0206 | 0.0927 | 0.1528 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
