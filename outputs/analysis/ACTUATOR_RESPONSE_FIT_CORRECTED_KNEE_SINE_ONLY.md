# Actuator Response Fit

## Executive Summary

primary_telemetry: `outputs/first_evidence/20260627T213827Z_corrected_knee_refit/actuator_sine_sweep_025_05_10_pitch_chain_combined.jsonl`
startup_ticks_ignored: `0`
selection_metric: `trimmed_rmse_95`
recommended_training_delay_ticks: `[3, 8]`
recommended_training_tau_s: `[0.06, 0.14]`
recommended_training_velocity_limit_rad_s: `[2.5, 4.7]`
confidence: `MEDIUM`

The fitted parameters are evidence for training randomization ranges, not a precise servo-internal model. The combined model is intended to capture delay, first-order lag, and effective velocity limiting visible in telemetry.

## Per-Joint Combined Fit

| joint | delay_ticks | delay_ms | tau_s | velocity_limit | selected | rmse | trimmed_rmse_95 | model_p95 | raw_p95 | target_range | actual_range | amp_ratio | target_vel_p95 | actual_vel_p95 | xcorr_lag | fit_quality | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_hip_pitch | 1 | 42.2 | 0.040 | 1.00 | 0.0023 | 0.0025 | 0.0023 | 0.0050 | 0.0069 | 0.0600 | 0.0590 | 0.983 | 0.0848 | 0.0964 | 1 | GOOD | velocity limit hit lower grid bound |
| left_knee | 1 | 42.2 | 0.040 | 1.00 | 0.0038 | 0.0039 | 0.0038 | 0.0050 | 0.0078 | 0.0600 | 0.0600 | 1.000 | 0.0893 | 0.0951 | 2 | GOOD | velocity limit hit lower grid bound |
| left_ankle | 1 | 42.2 | 0.040 | 1.00 | 0.0009 | 0.0012 | 0.0009 | 0.0022 | 0.0066 | 0.0600 | 0.0600 | 1.000 | 0.0898 | 0.1074 | 2 | GOOD | velocity limit hit lower grid bound |
| right_hip_pitch | 1 | 42.2 | 0.040 | 1.00 | 0.0034 | 0.0035 | 0.0034 | 0.0050 | 0.0069 | 0.0600 | 0.0630 | 1.050 | 0.0892 | 0.1077 | 1 | GOOD | velocity limit hit lower grid bound |
| right_knee | 1 | 42.2 | 0.040 | 1.00 | 0.0035 | 0.0037 | 0.0035 | 0.0060 | 0.0078 | 0.0600 | 0.0580 | 0.967 | 0.0899 | 0.0935 | 2 | GOOD | velocity limit hit lower grid bound |
| right_ankle | 1 | 42.2 | 0.040 | 1.00 | 0.0017 | 0.0019 | 0.0017 | 0.0029 | 0.0069 | 0.0600 | 0.0600 | 1.000 | 0.0874 | 0.0881 | 1 | GOOD | velocity limit hit lower grid bound |

## Model Family Comparison

| joint | delay_only_rmse | first_order_rmse | velocity_only_rmse | combined_rmse | support |
|---|---:|---:|---:|---:|---|
| left_hip_pitch | 0.0026 | 0.0026 | 0.0034 | 0.0025 | lag/delay improves over velocity-only |
| left_knee | 0.0040 | 0.0040 | 0.0047 | 0.0039 | lag/delay improves over velocity-only |
| left_ankle | 0.0014 | 0.0013 | 0.0026 | 0.0012 | lag/velocity improves over delay-only; delay improves over lag-only; lag/delay improves over velocity-only |
| right_hip_pitch | 0.0036 | 0.0036 | 0.0042 | 0.0035 | lag/delay improves over velocity-only |
| right_knee | 0.0038 | 0.0038 | 0.0045 | 0.0037 | lag/delay improves over velocity-only |
| right_ankle | 0.0021 | 0.0020 | 0.0030 | 0.0019 | lag/delay improves over velocity-only |

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
