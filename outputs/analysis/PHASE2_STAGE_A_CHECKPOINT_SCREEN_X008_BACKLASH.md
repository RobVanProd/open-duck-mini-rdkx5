# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `s655k` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0165 | 0.2058 | 0.0909 | 0.1520 | 1.5471 | 0.0000 | 0.1730 |
| `s1310k` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0173 | 0.2165 | 0.0933 | 0.1520 | 1.5652 | 0.0000 | 0.1738 |
| `s1966k` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0133 | 0.1659 | 0.0898 | 0.1520 | 1.5195 | 0.0000 | 0.1708 |
| `s2621k` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0143 | 0.1789 | 0.0926 | 0.1520 | 1.5324 | 0.0000 | 0.1689 |
| `s3277k` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0154 | 0.1919 | 0.0933 | 0.1520 | 1.5314 | 0.0000 | 0.1680 |
| `s3932k` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0118 | 0.1478 | 0.0893 | 0.1520 | 1.5418 | 0.0000 | 0.1740 |
| `s4588k` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0109 | 0.1365 | 0.0818 | 0.1520 | 1.5507 | 0.0000 | 0.1693 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `s655k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.2058 | 0.0165 | 0.0909 | 0.1520 | 0.0000 |
| `s1310k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.2165 | 0.0173 | 0.0933 | 0.1520 | 0.0000 |
| `s1966k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.1659 | 0.0133 | 0.0898 | 0.1520 | 0.0000 |
| `s2621k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.1789 | 0.0143 | 0.0926 | 0.1520 | 0.0000 |
| `s3277k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.1919 | 0.0154 | 0.0933 | 0.1520 | 0.0000 |
| `s3932k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.1478 | 0.0118 | 0.0893 | 0.1520 | 0.0000 |
| `s4588k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.1365 | 0.0109 | 0.0818 | 0.1520 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
