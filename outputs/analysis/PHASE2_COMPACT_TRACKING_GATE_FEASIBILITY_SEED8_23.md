# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `1.0`
seeds: `[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `None`
reset_settle_ticks: `0`
reset_mode: `playground`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `bounded_teacher` | 8 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0603 | 0.7534 | 0.1006 | 0.1474 | 1.8097 | 0.0000 | 0.0000 | 0.2909 | 0.0105 | 1 | 0.0004 | 14.0000 | 84.0000 | 0 | NA |
| `bounded_teacher` | 9 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.4245 | -5.3067 | 0.0627 | 0.0506 | 1.6191 | 0.0000 | 0.0000 | 0.2674 | 0.0227 | 2 | 0.0199 | 35.2941 | 55.8824 | 0 | NA |
| `bounded_teacher` | 10 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0633 | 0.7913 | 0.0952 | 0.1507 | 1.8669 | 0.0000 | 0.0000 | 0.1909 | 0.0094 | 1 | 0.0027 | 18.0000 | 82.0000 | 0 | NA |
| `bounded_teacher` | 11 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0141 | 0.1763 | 0.1501 | 0.1560 | 1.7467 | 0.0000 | 0.0000 | 0.2603 | 0.0087 | 3 | 0.0072 | 48.0000 | 52.0000 | 0 | NA |
| `bounded_teacher` | 12 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | -0.3828 | -4.7850 | 0.0440 | 0.0728 | 1.7164 | 0.0000 | 0.0000 | 0.2449 | 0.0226 | 2 | 0.0070 | 45.7143 | 48.5714 | 0 | NA |
| `bounded_teacher` | 13 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.1070 | -1.3378 | 0.2165 | 0.1561 | 1.4550 | 0.0000 | 0.0000 | 0.2102 | 0.0074 | 0 | 0.0000 | 26.0000 | 74.0000 | 0 | NA |
| `bounded_teacher` | 14 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 42 | `fall_or_nan` | -0.0749 | -0.9358 | 0.1787 | 0.0919 | 1.4086 | 0.0000 | 0.0000 | 0.3631 | 0.0155 | 1 | 0.0217 | 92.8571 | 0.0000 | 0 | NA |
| `bounded_teacher` | 15 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0090 | -0.1125 | 0.0728 | 0.1568 | 1.7742 | 0.0000 | 0.0000 | 0.2225 | 0.0051 | 2 | 0.0045 | 64.0000 | 32.0000 | 0 | NA |
| `bounded_teacher` | 16 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0610 | -0.7629 | 0.2647 | 0.1547 | 1.7449 | 0.0000 | 0.0000 | 0.1806 | 0.0159 | 0 | 0.0000 | 12.0000 | 88.0000 | 0 | NA |
| `bounded_teacher` | 17 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0101 | 0.1257 | 0.0230 | 0.1527 | 1.6491 | 0.0000 | 0.0000 | 0.1563 | 0.0052 | 0 | 0.0000 | 6.0000 | 94.0000 | 0 | NA |
| `bounded_teacher` | 18 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0595 | 0.7434 | 0.1066 | 0.1516 | 2.0000 | 0.0000 | 0.0000 | 0.2238 | 0.0109 | 1 | 0.0013 | 20.0000 | 80.0000 | 0 | NA |
| `bounded_teacher` | 19 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | -0.0783 | -0.9787 | 0.1629 | 0.0797 | 1.8774 | 0.0000 | 0.0000 | 0.6053 | 0.0352 | 1 | 0.0303 | 59.3750 | 9.3750 | 0 | NA |
| `bounded_teacher` | 20 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 28 | `fall_or_nan` | 0.0128 | 0.1597 | 0.3627 | 0.0733 | 1.8058 | 0.0000 | 0.0000 | 0.4216 | 0.0068 | 1 | 0.0318 | 82.1429 | 0.0000 | 0 | NA |
| `bounded_teacher` | 21 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0100 | 0.1252 | 0.0447 | 0.1517 | 1.7202 | 0.0000 | 0.0000 | 0.2157 | 0.0027 | 0 | 0.0000 | 14.0000 | 86.0000 | 0 | NA |
| `bounded_teacher` | 22 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0456 | 0.5694 | 0.0816 | 0.1527 | 1.7413 | 0.0000 | 0.0000 | 0.2730 | 0.0058 | 0 | 0.0000 | 10.0000 | 90.0000 | 0 | NA |
| `bounded_teacher` | 23 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0012 | -0.0155 | 0.1493 | 0.1555 | 1.8283 | 0.0000 | 0.0000 | 0.1761 | 0.0078 | 0 | 0.0000 | 22.0000 | 78.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `bounded_teacher` | 16 | 5 | 11 | 45.0625 | 28 | 50 | -0.6744 | -0.0540 | 0.1322 | 0.1284 | 0.0000 | 0.0000 | 0.0120 | 0.9375 | 0.0079 | 35.5865 | 59.6143 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
