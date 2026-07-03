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
| `phase_mod_rate180` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0349 | 0.4365 | 0.1397 | 0.1522 | 1.7775 | 0.0000 | 0.0000 | 0.1890 | 0.0131 | 23 | 0.0127 | 29.2000 | 70.8000 | 12 | 0.9167 |
| `phase_mod_rate180` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0363 | 0.4538 | 0.1415 | 0.1522 | 1.7833 | 0.0000 | 0.1319 | 0.1879 | 0.0129 | 18 | 0.0119 | 29.0667 | 70.9333 | 13 | 1.0000 |
| `phase_mod_rate180` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0348 | 0.4349 | 0.1404 | 0.1522 | 1.7704 | 0.0000 | 0.1611 | 0.1875 | 0.0135 | 18 | 0.0095 | 28.4000 | 71.6000 | 13 | 0.9231 |
| `phase_mod_rate180` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0374 | 0.4670 | 0.1395 | 0.1522 | 1.7782 | 0.0000 | 0.0000 | 0.1855 | 0.0147 | 17 | 0.0131 | 29.7333 | 70.2667 | 13 | 1.0000 |
| `phase_mod_rate180` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0362 | 0.4529 | 0.1341 | 0.1522 | 1.7696 | 0.0000 | 0.0000 | 0.1832 | 0.0128 | 18 | 0.0148 | 31.3333 | 68.6667 | 12 | 1.0000 |
| `phase_mod_rate180` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0350 | 0.4376 | 0.1425 | 0.1522 | 1.7642 | 0.0000 | 0.0000 | 0.1865 | 0.0142 | 17 | 0.0122 | 28.2667 | 71.7333 | 13 | 1.0000 |
| `phase_mod_rate180` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0359 | 0.4491 | 0.1317 | 0.1522 | 1.7761 | 0.0000 | 0.0000 | 0.1855 | 0.0130 | 19 | 0.0149 | 28.6667 | 71.3333 | 13 | 0.9231 |
| `phase_mod_rate180` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0342 | 0.4270 | 0.1436 | 0.1522 | 1.7991 | 0.0000 | 0.0000 | 0.1874 | 0.0123 | 17 | 0.0146 | 28.6667 | 71.3333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate180` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.4448 | 0.0356 | 0.1391 | 0.1522 | 0.0000 | 0.0366 | 0.0133 | 18.3750 | 0.0130 | 29.1667 | 70.8333 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
