# Actuator Response Fit

## Executive Summary

primary_telemetry: `outputs/first_evidence/20260712T_fixed_target_gain_ab_run/fixed_target_gain_ab.jsonl`
startup_ticks_ignored: `10`
selection_metric: `p95_abs_error`
recommended_training_delay_ticks: `[3, 8]`
recommended_training_tau_s: `[0.06, 0.14]`
recommended_training_velocity_limit_rad_s: `[2.5, 4.7]`
confidence: `MEDIUM`

The fitted parameters are evidence for training randomization ranges, not a precise servo-internal model. The combined model is intended to capture delay, first-order lag, and effective velocity limiting visible in telemetry.

## Per-Joint Combined Fit

| joint | delay_ticks | delay_ms | tau_s | velocity_limit | selected | rmse | trimmed_rmse_95 | model_p95 | raw_p95 | target_range | actual_range | amp_ratio | target_vel_p95 | actual_vel_p95 | xcorr_lag | fit_quality | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_hip_pitch | 3 | 60.0 | 0.005 | 1.75 | 0.0120 | 0.0061 | 0.0052 | 0.0120 | 0.0687 | 0.1914 | 0.1970 | 1.029 | 1.3085 | 1.2951 | 3 | GOOD | tau_s hit lower grid bound |
| left_knee | 3 | 60.0 | 0.005 | 1.75 | 0.0116 | 0.0064 | 0.0056 | 0.0116 | 0.0668 | 0.1649 | 0.1480 | 0.898 | 1.5490 | 1.2485 | 3 | GOOD | tau_s hit lower grid bound |
| left_ankle | 3 | 60.0 | 0.010 | 1.50 | 0.0090 | 0.0046 | 0.0040 | 0.0090 | 0.0572 | 0.1419 | 0.1280 | 0.902 | 1.2473 | 1.0398 | 3 | GOOD | none |
| right_hip_pitch | 3 | 60.0 | 0.005 | 1.25 | 0.0104 | 0.0056 | 0.0049 | 0.0104 | 0.0524 | 0.1319 | 0.1210 | 0.918 | 1.1338 | 0.9511 | 3 | GOOD | tau_s hit lower grid bound |
| right_knee | 2 | 40.0 | 0.030 | 1.00 | 0.0074 | 0.0044 | 0.0041 | 0.0074 | 0.0412 | 0.1228 | 0.1090 | 0.888 | 0.8487 | 0.6999 | 3 | GOOD | none |
| right_ankle | 3 | 60.0 | 0.005 | 1.25 | 0.0086 | 0.0044 | 0.0039 | 0.0086 | 0.0519 | 0.1110 | 0.1160 | 1.045 | 1.0306 | 0.8998 | 3 | GOOD | tau_s hit lower grid bound |

## Model Family Comparison

| joint | delay_only_rmse | first_order_rmse | velocity_only_rmse | combined_rmse | support |
|---|---:|---:|---:|---:|---|
| left_hip_pitch | 0.0060 | 0.0161 | 0.0212 | 0.0061 | delay improves over lag-only; lag/delay improves over velocity-only |
| left_knee | 0.0066 | 0.0165 | 0.0193 | 0.0064 | delay improves over lag-only; lag/delay improves over velocity-only |
| left_ankle | 0.0048 | 0.0143 | 0.0190 | 0.0046 | delay improves over lag-only; lag/delay improves over velocity-only |
| right_hip_pitch | 0.0057 | 0.0124 | 0.0156 | 0.0056 | delay improves over lag-only; lag/delay improves over velocity-only |
| right_knee | 0.0046 | 0.0097 | 0.0163 | 0.0044 | delay improves over lag-only; lag/delay improves over velocity-only |
| right_ankle | 0.0045 | 0.0126 | 0.0173 | 0.0044 | delay improves over lag-only; lag/delay improves over velocity-only |

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
- Use `--selection-metric trimmed_rmse_95` or `--selection-metric p95_abs_error` to test whether stale-but-finite read outliers are biasing the fitted velocity ceiling.
- Do not use these numbers to tune runtime behavior directly; use them to configure sim/training experiments first.
