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
| `phase_mod_rate150` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0330 | 0.4121 | 0.1501 | 0.1529 | 1.5488 | 0.0000 | 0.0000 | 0.1864 | 0.0131 | 18 | 0.0145 | 26.4000 | 73.6000 | 12 | 0.9167 |
| `phase_mod_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0306 | 0.3827 | 0.1558 | 0.1529 | 1.5621 | 0.0000 | 0.0000 | 0.1890 | 0.0126 | 14 | 0.0109 | 23.3333 | 76.6667 | 13 | 1.0000 |
| `phase_mod_rate150` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0310 | 0.3877 | 0.1504 | 0.1529 | 1.5392 | 0.0000 | 0.0000 | 0.1857 | 0.0148 | 13 | 0.0194 | 25.6000 | 74.4000 | 13 | 0.9231 |
| `phase_mod_rate150` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0296 | 0.3703 | 0.1546 | 0.1529 | 1.5527 | 0.0000 | 0.0000 | 0.1873 | 0.0125 | 13 | 0.0210 | 25.0667 | 74.9333 | 13 | 1.0000 |
| `phase_mod_rate150` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0293 | 0.3661 | 0.1475 | 0.1529 | 1.5429 | 0.0000 | 0.0000 | 0.1867 | 0.0131 | 15 | 0.0193 | 24.5333 | 75.4667 | 12 | 1.0000 |
| `phase_mod_rate150` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0291 | 0.3634 | 0.1497 | 0.1529 | 1.5647 | 0.0000 | 0.0000 | 0.1871 | 0.0130 | 13 | 0.0151 | 24.6667 | 75.3333 | 13 | 1.0000 |
| `phase_mod_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0307 | 0.3835 | 0.1476 | 0.1529 | 1.5484 | 0.0000 | 0.0000 | 0.1883 | 0.0155 | 16 | 0.0151 | 25.7333 | 74.2667 | 13 | 0.9231 |
| `phase_mod_rate150` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0318 | 0.3976 | 0.1500 | 0.1529 | 1.5604 | 0.0000 | 0.0000 | 0.1883 | 0.0158 | 14 | 0.0156 | 26.2667 | 73.7333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3829 | 0.0306 | 0.1507 | 0.1529 | 0.0000 | 0.0000 | 0.0138 | 14.5000 | 0.0163 | 25.2000 | 74.8000 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
