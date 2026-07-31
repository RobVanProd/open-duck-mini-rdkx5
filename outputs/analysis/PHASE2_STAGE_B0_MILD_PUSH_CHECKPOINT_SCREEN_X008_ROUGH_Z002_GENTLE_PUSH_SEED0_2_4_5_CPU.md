# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 2, 4, 5]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.05`-`0.1`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0_163` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0327 | 0.4083 | 0.1435 | 0.1519 | 1.7690 | 0.0000 | 0.2038 | 0.0138 | 5 | 0.0108 | 20.4000 | 79.6000 | 4 | 0.7500 |
| `b0_163` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0346 | 0.4324 | 0.1344 | 0.1511 | 1.7710 | 0.0000 | 0.1982 | 0.0127 | 7 | 0.0071 | 24.0000 | 76.0000 | 4 | 0.7500 |
| `b0_163` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0359 | 0.4483 | 0.1377 | 0.1506 | 1.7941 | 0.0000 | 0.1940 | 0.0133 | 4 | 0.0071 | 17.6000 | 82.4000 | 4 | 0.7500 |
| `b0_163` | 5 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0377 | 0.4716 | 0.1426 | 0.1462 | 1.7606 | 0.0000 | 0.2033 | 0.0184 | 5 | 0.0127 | 18.8000 | 80.4000 | 4 | 1.0000 |
| `b0_327` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0332 | 0.4146 | 0.1440 | 0.1519 | 1.7794 | 0.0000 | 0.2049 | 0.0151 | 6 | 0.0101 | 20.0000 | 80.0000 | 4 | 0.7500 |
| `b0_327` | 2 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0343 | 0.4286 | 0.1402 | 0.1511 | 1.8091 | 0.0000 | 0.2008 | 0.0139 | 7 | 0.0053 | 26.0000 | 74.0000 | 4 | 0.7500 |
| `b0_327` | 4 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0329 | 0.4110 | 0.1324 | 0.1506 | 1.7931 | 0.0000 | 0.2050 | 0.0127 | 4 | 0.0095 | 17.6000 | 82.4000 | 4 | 0.7500 |
| `b0_327` | 5 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0351 | 0.4383 | 0.1282 | 0.1462 | 1.7806 | 0.0000 | 0.2057 | 0.0183 | 4 | 0.0106 | 18.0000 | 81.2000 | 4 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `b0_163` | 4 | 0 | 4 | 250.0000 | 250 | 250 | 0.4401 | 0.0352 | 0.1396 | 0.1500 | 0.0000 | 0.0145 | 5.2500 | 0.0095 | 20.2000 | 79.6000 | 4.0000 | 0.8125 |
| `b0_327` | 4 | 0 | 4 | 250.0000 | 250 | 250 | 0.4231 | 0.0338 | 0.1362 | 0.1500 | 0.0000 | 0.0150 | 5.2500 | 0.0089 | 20.4000 | 79.4000 | 4.0000 | 0.8125 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
