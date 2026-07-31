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
terrain_hfield_z_scale: `0.0026`
reset_settle_ticks: `0`
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
| `phase_mod_rate150` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0004 | NA | 0.0393 | 0.1523 | 0.1094 | 0.0000 | 0.0000 | 0.0368 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `phase_mod_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0002 | NA | 0.0278 | 0.1523 | 0.1050 | 0.0000 | 0.0000 | 0.0346 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `phase_mod_rate150` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0002 | NA | 0.0397 | 0.1523 | 0.0749 | 0.0000 | 0.0000 | 0.0374 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `phase_mod_rate150` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0002 | NA | 0.0356 | 0.1523 | 0.0897 | 0.0000 | 0.0000 | 0.0361 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `phase_mod_rate150` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0002 | NA | 0.0358 | 0.1523 | 0.1083 | 0.0000 | 0.0000 | 0.0358 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 1.0000 |
| `phase_mod_rate150` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0003 | NA | 0.0394 | 0.1523 | 0.0850 | 0.0000 | 0.0000 | 0.0366 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 1.0000 |
| `phase_mod_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0004 | NA | 0.0357 | 0.1523 | 0.0824 | 0.0000 | 0.0000 | 0.0364 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `phase_mod_rate150` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0001 | NA | 0.0352 | 0.1523 | 0.0552 | 0.0000 | 0.0000 | 0.0351 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0002 | 0.0361 | 0.1523 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
