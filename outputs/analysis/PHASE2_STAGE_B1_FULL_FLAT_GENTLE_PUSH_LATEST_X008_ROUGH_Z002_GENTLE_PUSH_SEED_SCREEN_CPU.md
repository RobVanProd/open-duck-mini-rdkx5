# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 2, 4, 5, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b1` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0048 | 0.0600 | 0.0657 | 0.1519 | 1.4679 | 0.0000 | 0.1727 | 0.0032 | 1 | 0.0006 | 2.4000 | 97.6000 | 4 | 0.7500 |
| `b1` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0143 | 0.1791 | 0.1198 | 0.1511 | 1.4481 | 0.0000 | 0.1776 | 0.0107 | 2 | 0.0062 | 7.6000 | 92.4000 | 4 | 0.7500 |
| `b1` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0095 | 0.1192 | 0.0409 | 0.1506 | 1.4404 | 0.0000 | 0.1618 | 0.0003 | 0 | 0.0000 | 1.2000 | 98.8000 | 4 | 0.7500 |
| `b1` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0167 | 0.2088 | 0.0958 | 0.1462 | 1.4560 | 0.0000 | 0.1763 | 0.0190 | 1 | 0.0037 | 2.4000 | 96.8000 | 4 | 1.0000 |
| `b1` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0097 | 0.1216 | 0.0919 | 0.1530 | 1.4817 | 0.0000 | 0.1675 | 0.0161 | 1 | 0.0153 | 7.2000 | 92.8000 | 4 | 1.0000 |
| `b1` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0048 | 0.0598 | 0.0793 | 0.1564 | 1.4613 | 0.0000 | 0.1654 | 0.0036 | 0 | 0.0000 | 2.0000 | 98.0000 | 3 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b1` | 6 | 0 | 6 | 250.0000 | 250 | 250 | 0.1247 | 0.0100 | 0.0822 | 0.1516 | 0.0000 | 0.0088 | 0.8333 | 0.0043 | 3.8000 | 96.0667 | 3.8333 | 0.8750 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
