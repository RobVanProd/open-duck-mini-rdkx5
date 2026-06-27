# Actuator Response Fit

## Executive Summary

primary_telemetry: `outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl`
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
| left_hip_pitch | 3 | 60.3 | 0.020 | 2.50 | 0.0120 | 0.0137 | 0.0120 | 0.0267 | 0.1850 | 0.3645 | 0.2990 | 0.820 | 5.2169 | 2.4889 | 4 | GOOD | tau_s hit lower grid bound |
| left_knee | 3 | 60.3 | 0.020 | 3.25 | 0.0110 | 0.0126 | 0.0110 | 0.0248 | 0.1968 | 0.3303 | 0.3020 | 0.914 | 3.6614 | 2.7882 | 3 | GOOD | tau_s hit lower grid bound |
| left_ankle | 3 | 60.3 | 0.020 | 2.75 | 0.0076 | 0.0089 | 0.0076 | 0.0166 | 0.1474 | 0.2524 | 0.1910 | 0.757 | 3.7867 | 2.1208 | 4 | GOOD | tau_s hit lower grid bound |
| right_hip_pitch | 3 | 60.3 | 0.020 | 2.25 | 0.0115 | 0.0134 | 0.0115 | 0.0259 | 0.1518 | 0.2384 | 0.2490 | 1.044 | 3.0992 | 2.2899 | 4 | GOOD | tau_s hit lower grid bound |
| right_knee | 3 | 60.3 | 0.020 | 2.75 | 0.0137 | 0.0163 | 0.0137 | 0.0335 | 0.2058 | 0.3206 | 0.3110 | 0.970 | 4.4553 | 2.9372 | 4 | GOOD | tau_s hit lower grid bound |
| right_ankle | 3 | 60.3 | 0.020 | 2.00 | 0.0099 | 0.0110 | 0.0099 | 0.0211 | 0.1448 | 0.2745 | 0.2300 | 0.838 | 3.5194 | 1.9909 | 4 | GOOD | tau_s hit lower grid bound |

## Model Family Comparison

| joint | delay_only_rmse | first_order_rmse | velocity_only_rmse | combined_rmse | support |
|---|---:|---:|---:|---:|---|
| left_hip_pitch | 0.0313 | 0.0443 | 0.0496 | 0.0137 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| left_knee | 0.0206 | 0.0517 | 0.0584 | 0.0126 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| left_ankle | 0.0209 | 0.0300 | 0.0358 | 0.0089 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_hip_pitch | 0.0210 | 0.0368 | 0.0400 | 0.0134 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_knee | 0.0286 | 0.0577 | 0.0634 | 0.0163 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_ankle | 0.0244 | 0.0349 | 0.0442 | 0.0110 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |

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
