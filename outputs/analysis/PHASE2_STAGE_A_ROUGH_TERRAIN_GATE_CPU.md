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
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 230 | `fall_or_nan` | 0.0977 | 1.2216 | 0.6196 | 0.0222 | 1.7572 | 0.0000 | 0.2018 | 0 | NA |
| `stage_a` | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0164 | 0.2046 | 0.1875 | 0.1570 | 1.8001 | 0.0000 | 0.2071 | 0 | NA |
| `stage_a` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 697 | `fall_or_nan` | 0.0453 | 0.5662 | 0.2924 | 0.0012 | 1.7712 | 0.0000 | 0.2019 | 0 | NA |
| `stage_a` | 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 71 | `fall_or_nan` | -0.2579 | -3.2238 | 0.1651 | 0.0805 | 1.6237 | 0.0000 | 0.1800 | 0 | NA |
| `stage_a` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0102 | 0.1271 | 0.0592 | 0.1522 | 1.7557 | 0.0000 | 0.1881 | 0 | NA |
| `stage_a` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 49 | `fall_or_nan` | -0.2895 | -3.6189 | 0.0533 | 0.0807 | 1.7642 | 0.0000 | 0.2505 | 0 | NA |
| `stage_a` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 697 | `fall_or_nan` | 0.0352 | 0.4405 | 0.2865 | 0.0151 | 1.7572 | 0.0000 | 0.1940 | 0 | NA |
| `stage_a` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0149 | 0.1868 | 0.1107 | 0.1565 | 1.7522 | 0.0000 | 0.1937 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `stage_a` | 8 | 5 | 3 | 499.2500 | 49 | 750 | -0.5120 | -0.0410 | 0.2218 | 0.0832 | 0.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
