# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[0, 5]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `cmdscale_hi0p90` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0216 | 0.2699 | 0.0826 | 0.1520 | 3.2984 | 0.2376 |
| `cmdscale_hi0p90` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 66 | `fall_or_nan` | -0.2237 | -2.7967 | 0.0769 | 0.0654 | 2.7954 | 0.2433 |
| `cmdscale_hi0p95` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0333 | 0.4164 | 0.0951 | 0.1520 | 3.6166 | 0.2547 |
| `cmdscale_hi0p95` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0325 | 0.4068 | 0.0947 | 0.1463 | 3.5993 | 0.2520 |
| `cmdscale_hi0p975` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0412 | 0.5144 | 0.1004 | 0.1520 | 3.7124 | 0.2579 |
| `cmdscale_hi0p975` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0403 | 0.5041 | 0.0976 | 0.1463 | 3.6977 | 0.2594 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cmdscale_hi0p90` | 2 | 1 | 1 | 283.0000 | 66 | 500 | -1.2634 | -0.1011 | 0.0797 | 0.1087 |
| `cmdscale_hi0p95` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.4116 | 0.0329 | 0.0949 | 0.1491 |
| `cmdscale_hi0p975` | 2 | 0 | 2 | 500.0000 | 500 | 500 | 0.5092 | 0.0407 | 0.0990 | 0.1492 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
