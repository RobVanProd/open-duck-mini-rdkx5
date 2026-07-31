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
| `limit198_step0` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0352 | 0.4403 | 0.1690 | 0.1578 | 1.7827 | 0.0000 | 0.3883 | 0.1802 | 0.0187 | 15 | 0.0165 | 27.0667 | 72.9333 | 12 | 0.9167 |
| `limit198_step0` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0338 | 0.4219 | 0.1696 | 0.1578 | 1.7551 | 0.0000 | 0.6278 | 0.1830 | 0.0134 | 18 | 0.0188 | 29.7333 | 70.2667 | 13 | 0.9231 |
| `limit198_step0` | 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0302 | 0.3778 | 0.1622 | 0.1578 | 1.7896 | 0.0000 | 0.4722 | 0.1804 | 0.0151 | 15 | 0.0201 | 27.7333 | 72.2667 | 13 | 0.9231 |
| `limit198_step0` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 587 | `fall_or_nan` | 0.0001 | 0.0015 | 0.2009 | 0.0815 | 1.7911 | 0.0000 | 0.5496 | 0.1797 | 0.0345 | 12 | 0.0206 | 25.0426 | 74.4463 | 10 | 0.9000 |
| `limit198_step0` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 318 | `fall_or_nan` | -0.0341 | -0.4263 | 0.1714 | 0.0622 | 1.8020 | 0.0000 | 0.8346 | 0.1755 | 0.0335 | 7 | 0.0195 | 20.4403 | 78.6164 | 4 | 0.7500 |
| `rate165_step0` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 153 | `fall_or_nan` | 0.1321 | 1.6518 | 0.8381 | 0.0021 | 1.6644 | 0.0000 | 0.1962 | 0.1890 | 0.0597 | 1 | 0.0029 | 7.8431 | 90.1961 | 2 | 0.5000 |
| `rate165_step0` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 154 | `fall_or_nan` | 0.1295 | 1.6188 | 0.8003 | 0.0152 | 1.6398 | 0.0000 | 0.0000 | 0.1894 | 0.0601 | 2 | 0.0037 | 7.7922 | 90.9091 | 2 | 0.5000 |
| `rate165_step0` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 153 | `fall_or_nan` | 0.1351 | 1.6893 | 0.8405 | 0.0035 | 1.6360 | 0.0000 | 0.5761 | 0.1900 | 0.0602 | 2 | 0.0096 | 11.1111 | 86.9281 | 2 | 0.5000 |
| `rate165_step0` | 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0217 | 0.2707 | 0.1820 | 0.1586 | 1.6207 | 0.0000 | 0.2985 | 0.1822 | 0.0140 | 7 | 0.0147 | 17.7333 | 82.2667 | 13 | 0.9231 |
| `rate165_step0` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0222 | 0.2775 | 0.2213 | 0.1582 | 1.6237 | 0.0000 | 0.1041 | 0.1826 | 0.0180 | 8 | 0.0242 | 19.3333 | 80.6667 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `limit198_step0` | 5 | 2 | 3 | 631.0000 | 318 | 750 | 0.1630 | 0.0130 | 0.1746 | 0.1234 | 0.0000 | 0.5745 | 0.0231 | 13.4000 | 0.0191 | 26.0032 | 73.7059 | 10.4000 | 0.8826 |
| `rate165_step0` | 5 | 3 | 2 | 392.0000 | 153 | 750 | 1.1016 | 0.0881 | 0.5764 | 0.0675 | 0.0000 | 0.2350 | 0.0424 | 4.0000 | 0.0110 | 12.7626 | 86.1933 | 5.8000 | 0.6646 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
