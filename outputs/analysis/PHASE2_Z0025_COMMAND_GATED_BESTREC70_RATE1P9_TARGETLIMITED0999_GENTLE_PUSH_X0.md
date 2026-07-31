# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0025`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0001 | NA | 0.0244 | 0.1519 | 2.7472 | 0.0000 | 0.0000 | 0.1936 | 0.0006 | 0 | 0.0000 | 1.6000 | 98.4000 | 12 | 0.9167 |
| `limited` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0014 | NA | 0.0578 | 0.1563 | 2.7472 | 0.0000 | 0.0000 | 0.1890 | 0.0036 | 0 | 0.0000 | 1.6000 | 98.2667 | 13 | 1.0000 |
| `limited` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0003 | NA | 0.0391 | 0.1513 | 2.7472 | 0.0000 | 0.0000 | 0.1942 | 0.0063 | 1 | 0.0038 | 2.1333 | 97.8667 | 13 | 0.9231 |
| `limited` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0026 | NA | 0.0360 | 0.1556 | 2.7472 | 0.0000 | 0.0000 | 0.1946 | 0.0003 | 0 | 0.0000 | 0.9333 | 99.0667 | 13 | 1.0000 |
| `limited` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0005 | NA | 0.0254 | 0.1505 | 2.7472 | 0.0000 | 0.0000 | 0.1938 | 0.0073 | 1 | 0.0039 | 1.8667 | 98.1333 | 12 | 1.0000 |
| `limited` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0010 | NA | 0.0190 | 0.1457 | 2.7472 | 0.0000 | 0.0000 | 0.1942 | 0.0196 | 3 | 0.0090 | 3.0667 | 96.6667 | 13 | 1.0000 |
| `limited` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0003 | NA | 0.0288 | 0.1530 | 2.7472 | 0.0000 | 0.0000 | 0.1917 | 0.0164 | 1 | 0.0136 | 1.7333 | 98.2667 | 13 | 0.9231 |
| `limited` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | -0.0007 | NA | 0.0333 | 0.1565 | 2.7472 | 0.0000 | 0.0000 | 0.1943 | 0.0005 | 0 | 0.0000 | 2.1333 | 97.8667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limited` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | -0.0004 | 0.0330 | 0.1526 | 0.0000 | 0.0000 | 0.0068 | 0.7500 | 0.0038 | 1.8833 | 98.0667 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
