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
seeds: `[0, 1, 2, 6, 7]`
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
| `iter21_seed67_w2_seed1_seed2` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0307 | 0.3842 | 0.1803 | 0.1580 | 1.5483 | 0.0000 | 0.0000 | 0.1802 | 0.0200 | 17 | 0.0236 | 28.5333 | 71.4667 | 12 | 0.9167 |
| `iter21_seed67_w2_seed1_seed2` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0294 | 0.3679 | 0.1722 | 0.1578 | 1.5496 | 0.0000 | 0.0000 | 0.1867 | 0.0149 | 18 | 0.0222 | 27.2000 | 72.8000 | 13 | 0.9231 |
| `iter21_seed67_w2_seed1_seed2` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0272 | 0.3398 | 0.1787 | 0.1573 | 1.5593 | 0.0000 | 0.0000 | 0.1840 | 0.0144 | 15 | 0.0249 | 26.5333 | 73.4667 | 13 | 0.9231 |
| `iter21_seed67_w2_seed1_seed2` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0248 | 0.3100 | 0.1816 | 0.1583 | 1.5644 | 0.0000 | 0.0000 | 0.1846 | 0.0153 | 14 | 0.0284 | 23.8667 | 76.1333 | 13 | 0.9231 |
| `iter21_seed67_w2_seed1_seed2` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 288 | `fall_or_nan` | -0.0440 | -0.5495 | 0.1713 | 0.0549 | 1.5588 | 0.0000 | 0.0000 | 0.1761 | 0.0340 | 6 | 0.0211 | 22.9167 | 76.3889 | 4 | 0.7500 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `iter21_seed67_w2_seed1_seed2` | 5 | 1 | 4 | 657.6000 | 288 | 750 | 0.1705 | 0.0136 | 0.1768 | 0.1373 | 0.0000 | 0.0000 | 0.0197 | 14.0000 | 0.0240 | 25.8100 | 74.0511 | 11.0000 | 0.8872 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
