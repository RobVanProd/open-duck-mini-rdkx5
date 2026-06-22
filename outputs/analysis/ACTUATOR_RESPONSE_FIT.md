# Actuator Response Fit

## Executive Summary

primary_telemetry: `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl`
startup_ticks_ignored: `50`
recommended_training_delay_ticks: `[3, 8]`
recommended_training_tau_s: `[0.06, 0.14]`
recommended_training_velocity_limit_rad_s: `[2.5, 4.7]`
confidence: `MEDIUM`

The fitted parameters are evidence for training randomization ranges, not a precise servo-internal model. The combined model is intended to capture delay, first-order lag, and effective velocity limiting visible in telemetry.

## Per-Joint Combined Fit

| joint | delay_ticks | delay_ms | tau_s | velocity_limit | rmse | model_p95 | raw_p95 | target_range | actual_range | amp_ratio | target_vel_p95 | actual_vel_p95 | xcorr_lag | fit_quality | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_hip_pitch | 3 | 60.3 | 0.020 | 2.50 | 0.0149 | 0.0252 | 0.1736 | 0.3493 | 0.2760 | 0.790 | 5.2170 | 2.4047 | 4 | GOOD | tau_s hit lower grid bound |
| left_knee | 3 | 60.3 | 0.020 | 3.50 | 0.0169 | 0.0333 | 0.1793 | 0.3430 | 0.3230 | 0.942 | 3.7814 | 2.9371 | 3 | GOOD | tau_s hit lower grid bound |
| left_ankle | 3 | 60.3 | 0.020 | 3.00 | 0.0106 | 0.0193 | 0.1325 | 0.2444 | 0.2030 | 0.831 | 3.7399 | 2.1407 | 3 | GOOD | tau_s hit lower grid bound |
| right_hip_pitch | 3 | 60.3 | 0.020 | 3.75 | 0.0155 | 0.0286 | 0.1661 | 0.2492 | 0.2700 | 1.083 | 3.1013 | 2.6398 | 3 | GOOD | tau_s hit lower grid bound |
| right_knee | 3 | 60.3 | 0.020 | 3.00 | 0.0193 | 0.0348 | 0.2062 | 0.3608 | 0.3210 | 0.890 | 4.8109 | 3.1864 | 3 | GOOD | tau_s hit lower grid bound |
| right_ankle | 3 | 60.3 | 0.020 | 2.25 | 0.0144 | 0.0273 | 0.1428 | 0.2796 | 0.2470 | 0.883 | 3.5230 | 2.1408 | 3 | GOOD | tau_s hit lower grid bound |

## Model Family Comparison

| joint | delay_only_rmse | first_order_rmse | velocity_only_rmse | combined_rmse | support |
|---|---:|---:|---:|---:|---|
| left_hip_pitch | 0.0286 | 0.0411 | 0.0466 | 0.0149 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| left_knee | 0.0191 | 0.0483 | 0.0539 | 0.0169 | delay improves over lag-only; lag/delay improves over velocity-only |
| left_ankle | 0.0184 | 0.0302 | 0.0366 | 0.0106 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_hip_pitch | 0.0189 | 0.0406 | 0.0406 | 0.0155 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_knee | 0.0301 | 0.0617 | 0.0680 | 0.0193 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_ankle | 0.0227 | 0.0370 | 0.0445 | 0.0144 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |

## Recommended Training Ranges

| parameter | range | reason |
|---|---:|---|
| delay_ticks | `3-8` | covers replay cross-correlation lag and expected training stress range |
| tau_s | `0.06-0.14` | matches measured effective 80-130 ms behavior and bridge spec |
| effective_velocity_limit_rad_s | `2.5-4.7` | below/near ST3215 no-load speed; stress-tests loaded gait |
| per_joint_asymmetry | enabled | fit and tracking differ across hip/knee/ankle and left/right |

## Warnings

- Fit quality is limited by telemetry cadence and by using commanded target/feedback logs, not servo-internal current-loop data.
- CRC/read errors remain a watch item, but this fit does not model packet-level dropouts.
- Do not use these numbers to tune runtime behavior directly; use them to configure sim/training experiments first.

## Comparison Telemetry

comparison_telemetry: `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x0_after_wire_routing.jsonl`
bus: `{'read_error_count': 8, 'write_error_count': 0, 'last_error': 'read_present_position: Checksum error'}`

| joint | raw_p95 | target_vel_p95 | combined_rmse | combined_p95 |
|---|---:|---:|---:|---:|
| left_hip_pitch | 0.0105 | 0.1241 | 0.0021 | 0.0046 |
| left_knee | 0.0080 | 0.0977 | 0.0033 | 0.0049 |
| left_ankle | 0.0073 | 0.1101 | 0.0017 | 0.0029 |
| right_hip_pitch | 0.0114 | 0.1241 | 0.0031 | 0.0052 |
| right_knee | 0.0053 | 0.0924 | 0.0016 | 0.0024 |
| right_ankle | 0.0028 | 0.0454 | 0.0006 | 0.0011 |
