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
seeds: `[24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]`
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
trace_seeds: `[24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]`
trace_full_obs: `True`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heldout_baseline` | 24 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0396 | 0.4956 | 0.1020 | 0.1528 | 1.7508 | 0.0000 | 0.0000 | 0.1708 | 0.0060 | 1 | 0.0007 | 10.0000 | 90.0000 | 0 | NA |
| `heldout_baseline` | 25 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0010 | 0.0127 | 0.1058 | 0.1558 | 1.5628 | 0.0000 | 0.0000 | 0.2062 | 0.0071 | 2 | 0.0042 | 36.0000 | 62.0000 | 0 | NA |
| `heldout_baseline` | 26 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0135 | 0.1682 | 0.1005 | 0.1577 | 1.5248 | 0.0000 | 0.0000 | 0.2166 | 0.0079 | 2 | 0.0013 | 30.0000 | 66.0000 | 0 | NA |
| `heldout_baseline` | 27 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0302 | 0.3779 | 0.1739 | 0.1542 | 1.6015 | 0.0000 | 0.0000 | 0.3401 | 0.0201 | 2 | 0.0102 | 62.0000 | 38.0000 | 0 | NA |
| `heldout_baseline` | 28 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0235 | -0.2935 | 0.1716 | 0.1579 | 1.5382 | 0.0000 | 0.0000 | 0.3065 | 0.0217 | 2 | 0.0058 | 74.0000 | 24.0000 | 0 | NA |
| `heldout_baseline` | 29 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0175 | 0.2191 | 0.0994 | 0.1541 | 1.6458 | 0.0000 | 0.0000 | 0.1652 | 0.0027 | 0 | 0.0000 | 16.0000 | 84.0000 | 0 | NA |
| `heldout_baseline` | 30 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0295 | 0.3690 | 0.0362 | 0.1543 | 1.5196 | 0.0000 | 0.0000 | 0.2288 | 0.0063 | 1 | 0.0093 | 22.0000 | 78.0000 | 0 | NA |
| `heldout_baseline` | 31 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0078 | 0.0970 | 0.0711 | 0.1534 | 1.6025 | 0.0000 | 0.0000 | 0.1632 | 0.0051 | 1 | 0.0045 | 18.0000 | 82.0000 | 0 | NA |
| `heldout_baseline` | 32 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.0093 | -0.1157 | 0.2108 | 0.1566 | 1.6478 | 0.0000 | 0.0000 | 0.2124 | 0.0093 | 2 | 0.0010 | 26.0000 | 70.0000 | 0 | NA |
| `heldout_baseline` | 33 | `HOLD_CANDIDATE_TRACKING` | 50 | `duration_complete` | 0.0435 | 0.5440 | 0.0502 | 0.1500 | 1.6210 | 0.0000 | 0.0000 | 0.2011 | 0.0025 | 0 | 0.0000 | 10.0000 | 90.0000 | 0 | NA |
| `heldout_baseline` | 34 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | -0.2924 | -3.6550 | 0.0158 | 0.0846 | 1.5831 | 0.0000 | 0.0000 | 0.2435 | 0.0264 | 0 | 0.0000 | 6.0000 | 88.0000 | 0 | NA |
| `heldout_baseline` | 35 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0138 | 0.1723 | 0.0969 | 0.1523 | 1.6697 | 0.0000 | 0.0000 | 0.2042 | 0.0083 | 1 | 0.0019 | 22.0000 | 78.0000 | 0 | NA |
| `heldout_baseline` | 36 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 28 | `fall_or_nan` | -0.1029 | -1.2862 | 0.1238 | 0.0795 | 1.6047 | 0.0000 | 0.0000 | 0.4166 | 0.0135 | 1 | 0.0007 | 82.1429 | 7.1429 | 0 | NA |
| `heldout_baseline` | 37 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 27 | `fall_or_nan` | -0.0580 | -0.7250 | 0.2157 | 0.0860 | 1.8200 | 0.0000 | 0.0000 | 0.3826 | 0.0343 | 1 | 0.0608 | 85.1852 | 0.0000 | 0 | NA |
| `heldout_baseline` | 38 | `PASS_CANDIDATE_SIM_GATE` | 50 | `duration_complete` | 0.0554 | 0.6925 | 0.0817 | 0.1530 | 1.6534 | 0.0000 | 0.0000 | 0.1735 | 0.0083 | 1 | 0.0033 | 18.0000 | 82.0000 | 0 | NA |
| `heldout_baseline` | 39 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 50 | `duration_complete` | 0.0180 | 0.2252 | 0.0565 | 0.1555 | 1.6308 | 0.0000 | 0.0000 | 0.1966 | 0.0040 | 0 | 0.0000 | 6.0000 | 92.0000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `heldout_baseline` | 16 | 2 | 14 | 47.1875 | 27 | 50 | -0.1689 | -0.0135 | 0.1070 | 0.1411 | 0.0000 | 0.0000 | 0.0115 | 1.0625 | 0.0065 | 32.7080 | 64.4464 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
