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
eval_push_magnitude: `0.1`-`0.15`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.005`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0253 | 0.3157 | 0.1623 | 0.1529 | 1.5827 | 0.0000 | 0.0000 | 0.1861 | 0.0160 | 11 | 0.0166 | 22.1333 | 77.8667 | 12 | 0.9167 |
| `phase_mod_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0272 | 0.3406 | 0.1495 | 0.1529 | 1.5586 | 0.0000 | 0.0000 | 0.1829 | 0.0132 | 13 | 0.0097 | 22.4000 | 77.6000 | 13 | 1.0000 |
| `phase_mod_rate150` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0308 | 0.3849 | 0.1529 | 0.1529 | 1.5652 | 0.0000 | 0.0000 | 0.1861 | 0.0146 | 17 | 0.0155 | 28.1333 | 71.8667 | 13 | 0.9231 |
| `phase_mod_rate150` | 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0289 | 0.3612 | 0.1531 | 0.1529 | 1.5550 | 0.0000 | 0.0006 | 0.1907 | 0.0127 | 15 | 0.0238 | 23.7333 | 76.2667 | 13 | 1.0000 |
| `phase_mod_rate150` | 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0293 | 0.3659 | 0.1546 | 0.1529 | 1.5516 | 0.0000 | 0.1537 | 0.1854 | 0.0135 | 13 | 0.0172 | 24.1333 | 75.8667 | 12 | 1.0000 |
| `phase_mod_rate150` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0266 | 0.3319 | 0.1552 | 0.1529 | 1.5527 | 0.0000 | 0.0000 | 0.1872 | 0.0127 | 10 | 0.0188 | 20.9333 | 79.0667 | 13 | 1.0000 |
| `phase_mod_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3559 | 0.1395 | 0.1529 | 1.5611 | 0.0000 | 0.0000 | 0.1874 | 0.0165 | 15 | 0.0128 | 23.8667 | 76.1333 | 13 | 0.9231 |
| `phase_mod_rate150` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0296 | 0.3700 | 0.1618 | 0.1529 | 1.5647 | 0.0000 | 0.0503 | 0.1882 | 0.0150 | 12 | 0.0231 | 23.8667 | 76.1333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3532 | 0.0283 | 0.1536 | 0.1529 | 0.0000 | 0.0256 | 0.0143 | 13.2500 | 0.0172 | 23.6500 | 76.3500 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
