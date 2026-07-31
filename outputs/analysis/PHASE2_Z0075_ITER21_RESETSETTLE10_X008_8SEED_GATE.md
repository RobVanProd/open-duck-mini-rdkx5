# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_rate150_settle10` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0271 | 0.3391 | 0.1628 | 0.1593 | 1.6164 | 0.0000 | 0.0000 | 0.1827 | 0.0140 | 14 | 0.0208 | 24.9333 | 75.0667 | 12 | 0.9167 |
| `iter21_rate150_settle10` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0317 | 0.3964 | 0.1916 | 0.1576 | 1.6221 | 0.0000 | 0.0583 | 0.1850 | 0.0187 | 14 | 0.0179 | 24.5333 | 75.4667 | 13 | 0.9231 |
| `iter21_rate150_settle10` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0258 | 0.3225 | 0.1716 | 0.1589 | 1.6214 | 0.0000 | 0.0000 | 0.1839 | 0.0140 | 15 | 0.0213 | 25.7333 | 74.2667 | 13 | 0.9231 |
| `iter21_rate150_settle10` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0281 | 0.3514 | 0.1589 | 0.1587 | 1.6129 | 0.0000 | 0.0097 | 0.1791 | 0.0147 | 16 | 0.0144 | 24.8000 | 75.2000 | 13 | 0.9231 |
| `iter21_rate150_settle10` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0241 | 0.3014 | 0.1655 | 0.1593 | 1.6522 | 0.0000 | 0.0000 | 0.1776 | 0.0136 | 12 | 0.0126 | 23.8667 | 76.1333 | 12 | 0.9167 |
| `iter21_rate150_settle10` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 599 | `fall_or_nan` | -0.0054 | -0.0672 | 0.1735 | 0.0630 | 1.6282 | 0.0000 | 0.0000 | 0.1786 | 0.0337 | 11 | 0.0170 | 23.2053 | 76.4608 | 10 | 0.9000 |
| `iter21_rate150_settle10` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3567 | 0.1662 | 0.1588 | 1.6211 | 0.0000 | 0.0000 | 0.1835 | 0.0162 | 10 | 0.0227 | 26.0000 | 74.0000 | 13 | 0.9231 |
| `iter21_rate150_settle10` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0311 | 0.3886 | 0.1480 | 0.1593 | 1.6216 | 0.0000 | 0.0000 | 0.1815 | 0.0147 | 15 | 0.0160 | 25.0667 | 74.9333 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_rate150_settle10` | 8 | 1 | 7 | 731.1250 | 599 | 750 | 0.2986 | 0.0239 | 0.1673 | 0.1469 | 0.0000 | 0.0085 | 0.0175 | 13.3750 | 0.0178 | 24.7673 | 75.1909 | 12.0000 | 0.9157 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
