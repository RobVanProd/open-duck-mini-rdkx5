# Actuator Response Fit

## Executive Summary

primary_telemetry: `/tmp/corrected_dynamic_replay_exclude_read_events_pm2.jsonl`
startup_ticks_ignored: `50`
selection_metric: `trimmed_rmse_95`
recommended_training_delay_ticks: `[3, 8]`
recommended_training_tau_s: `[0.06, 0.14]`
recommended_training_velocity_limit_rad_s: `[2.5, 4.7]`
confidence: `MEDIUM`

The fitted parameters are evidence for training randomization ranges, not a precise servo-internal model. The combined model is intended to capture delay, first-order lag, and effective velocity limiting visible in telemetry.

## Per-Joint Combined Fit

| joint | delay_ticks | delay_ms | tau_s | velocity_limit | selected | rmse | trimmed_rmse_95 | model_p95 | raw_p95 | target_range | actual_range | amp_ratio | target_vel_p95 | actual_vel_p95 | xcorr_lag | fit_quality | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_hip_pitch | 3 | 60.3 | 0.020 | 2.75 | 0.0144 | 0.0262 | 0.0144 | 0.0492 | 0.1898 | 0.3645 | 0.2990 | 0.820 | 5.2171 | 2.7383 | 3 | GOOD | tau_s hit lower grid bound |
| left_knee | 3 | 60.3 | 0.020 | 6.00 | 0.0171 | 0.0384 | 0.0171 | 0.0895 | 0.1974 | 0.3303 | 0.3020 | 0.914 | 3.9695 | 2.9870 | 3 | USEFUL | tau_s hit lower grid bound, velocity limit hit upper grid bound |
| left_ankle | 3 | 60.3 | 0.020 | 2.75 | 0.0091 | 0.0167 | 0.0091 | 0.0301 | 0.1484 | 0.2524 | 0.1910 | 0.757 | 4.2537 | 2.3547 | 3 | GOOD | tau_s hit lower grid bound |
| right_hip_pitch | 3 | 60.3 | 0.020 | 2.25 | 0.0139 | 0.0246 | 0.0139 | 0.0419 | 0.1515 | 0.2384 | 0.2490 | 1.044 | 3.3179 | 2.3053 | 3 | GOOD | tau_s hit lower grid bound |
| right_knee | 3 | 60.3 | 0.020 | 2.75 | 0.0190 | 0.0351 | 0.0190 | 0.0845 | 0.2043 | 0.3206 | 0.3110 | 0.970 | 4.7246 | 3.0367 | 3 | USEFUL | tau_s hit lower grid bound |
| right_ankle | 3 | 60.3 | 0.020 | 2.25 | 0.0127 | 0.0231 | 0.0127 | 0.0507 | 0.1448 | 0.2738 | 0.2300 | 0.840 | 3.7581 | 1.9916 | 3 | USEFUL | tau_s hit lower grid bound |

## Model Family Comparison

| joint | delay_only_rmse | first_order_rmse | velocity_only_rmse | combined_rmse | support |
|---|---:|---:|---:|---:|---|
| left_hip_pitch | 0.0376 | 0.0465 | 0.0512 | 0.0262 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| left_knee | 0.0402 | 0.0544 | 0.0601 | 0.0384 | delay improves over lag-only; lag/delay improves over velocity-only |
| left_ankle | 0.0253 | 0.0304 | 0.0358 | 0.0167 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_hip_pitch | 0.0278 | 0.0383 | 0.0416 | 0.0246 | delay improves over lag-only; lag/delay improves over velocity-only |
| right_knee | 0.0453 | 0.0611 | 0.0656 | 0.0351 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_ankle | 0.0291 | 0.0379 | 0.0459 | 0.0231 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |

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
