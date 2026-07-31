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
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0026`
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
| `phase_mod_rate150` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0314 | 0.3929 | 0.1353 | 0.1522 | 1.5342 | 0.0000 | 0.0000 | 0.1868 | 0.0128 | 16 | 0.0078 | 27.0667 | 72.9333 | 12 | 0.9167 |
| `phase_mod_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0291 | 0.3636 | 0.1330 | 0.1522 | 1.5479 | 0.0000 | 0.0000 | 0.1861 | 0.0120 | 14 | 0.0152 | 24.4000 | 75.6000 | 13 | 1.0000 |
| `phase_mod_rate150` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0307 | 0.3835 | 0.1338 | 0.1522 | 1.5353 | 0.0000 | 0.0000 | 0.1853 | 0.0119 | 16 | 0.0135 | 28.2667 | 71.7333 | 13 | 0.9231 |
| `phase_mod_rate150` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0296 | 0.3700 | 0.1332 | 0.1522 | 1.5437 | 0.0000 | 0.0000 | 0.1869 | 0.0124 | 14 | 0.0120 | 25.2000 | 74.8000 | 13 | 1.0000 |
| `phase_mod_rate150` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0316 | 0.3953 | 0.1346 | 0.1522 | 1.5415 | 0.0000 | 0.0000 | 0.1853 | 0.0120 | 14 | 0.0144 | 26.8000 | 73.2000 | 12 | 1.0000 |
| `phase_mod_rate150` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0296 | 0.3703 | 0.1472 | 0.1522 | 1.5352 | 0.0000 | 0.0000 | 0.1892 | 0.0121 | 13 | 0.0145 | 24.6667 | 75.3333 | 13 | 1.0000 |
| `phase_mod_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0309 | 0.3865 | 0.1305 | 0.1522 | 1.5513 | 0.0000 | 0.0000 | 0.1886 | 0.0116 | 14 | 0.0121 | 25.7333 | 74.2667 | 13 | 0.9231 |
| `phase_mod_rate150` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3827 | 0.1357 | 0.1522 | 1.5352 | 0.0000 | 0.0000 | 0.1873 | 0.0121 | 15 | 0.0222 | 26.2667 | 73.7333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3806 | 0.0304 | 0.1354 | 0.1522 | 0.0000 | 0.0000 | 0.0121 | 14.5000 | 0.0140 | 26.0500 | 73.9500 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
