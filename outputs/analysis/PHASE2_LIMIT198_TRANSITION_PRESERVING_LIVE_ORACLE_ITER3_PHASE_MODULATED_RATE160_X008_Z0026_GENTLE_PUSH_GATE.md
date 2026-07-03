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
| `phase_mod_rate160` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0301 | 0.3768 | 0.1365 | 0.1522 | 1.6179 | 0.0000 | 0.0000 | 0.1852 | 0.0131 | 14 | 0.0139 | 26.8000 | 73.2000 | 12 | 0.9167 |
| `phase_mod_rate160` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0313 | 0.3908 | 0.1295 | 0.1522 | 1.6052 | 0.0000 | 0.0000 | 0.1857 | 0.0123 | 16 | 0.0118 | 26.2667 | 73.7333 | 13 | 1.0000 |
| `phase_mod_rate160` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0305 | 0.3815 | 0.1319 | 0.1522 | 1.6218 | 0.0000 | 0.0000 | 0.1853 | 0.0121 | 13 | 0.0140 | 26.0000 | 74.0000 | 13 | 0.9231 |
| `phase_mod_rate160` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0299 | 0.3731 | 0.1336 | 0.1522 | 1.6113 | 0.0000 | 0.0000 | 0.1835 | 0.0128 | 16 | 0.0113 | 26.4000 | 73.6000 | 13 | 1.0000 |
| `phase_mod_rate160` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0309 | 0.3856 | 0.1348 | 0.1522 | 1.6064 | 0.0000 | 0.0000 | 0.1865 | 0.0137 | 15 | 0.0200 | 25.6000 | 74.4000 | 12 | 1.0000 |
| `phase_mod_rate160` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0309 | 0.3862 | 0.1405 | 0.1522 | 1.6341 | 0.0000 | 0.0000 | 0.1879 | 0.0123 | 17 | 0.0129 | 26.0000 | 74.0000 | 13 | 1.0000 |
| `phase_mod_rate160` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0297 | 0.3715 | 0.1363 | 0.1522 | 1.6230 | 0.0000 | 0.0000 | 0.1858 | 0.0123 | 11 | 0.0122 | 25.3333 | 74.6667 | 13 | 0.9231 |
| `phase_mod_rate160` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0305 | 0.3807 | 0.1394 | 0.1522 | 1.6269 | 0.0000 | 0.0000 | 0.1875 | 0.0129 | 16 | 0.0148 | 27.3333 | 72.6667 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate160` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3808 | 0.0305 | 0.1353 | 0.1522 | 0.0000 | 0.0000 | 0.0127 | 14.7500 | 0.0139 | 26.2167 | 73.7833 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
