# Actuator Response Fit Compare

status: `PASS_ACTUATOR_FIT_COMPARE_READY`

Offline comparison only. No robot tests, SSH, deployment, training, or runtime behavior changes were performed.

## Inputs

- old fit: `outputs/analysis/actuator_response_fit.json`
- old telemetry: `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl`
- new fit: `outputs/analysis/actuator_response_fit_corrected_knee_sine_only.json`
- new telemetry: `outputs/first_evidence/20260627T213827Z_corrected_knee_refit/actuator_sine_sweep_025_05_10_pitch_chain_combined.jsonl`

## Per-Joint Delta

| joint | delay old->new | tau old->new | vel old->new | model p95 old->new | raw p95 old->new | target vel p95 old->new | actual vel p95 old->new | quality old->new | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_ankle | 3->1 (-2) | 0.020->0.040 (0.020) | 3.00->1.00 (-2.00) | 0.0193->0.0022 (-0.0170) | 0.1325->0.0066 (-0.1259) | 3.7399->0.0898 (-3.6501) | 2.1407->0.1074 (-2.0334) | `GOOD`->`GOOD` | velocity limit hit lower grid bound |
| left_hip_pitch | 3->1 (-2) | 0.020->0.040 (0.020) | 2.50->1.00 (-1.50) | 0.0252->0.0050 (-0.0202) | 0.1736->0.0069 (-0.1667) | 5.2170->0.0848 (-5.1322) | 2.4047->0.0964 (-2.3082) | `GOOD`->`GOOD` | velocity limit hit lower grid bound |
| left_knee | 3->1 (-2) | 0.020->0.040 (0.020) | 3.50->1.00 (-2.50) | 0.0333->0.0050 (-0.0283) | 0.1793->0.0078 (-0.1715) | 3.7814->0.0893 (-3.6920) | 2.9371->0.0951 (-2.8420) | `GOOD`->`GOOD` | velocity limit hit lower grid bound |
| right_ankle | 3->1 (-2) | 0.020->0.040 (0.020) | 2.25->1.00 (-1.25) | 0.0273->0.0029 (-0.0244) | 0.1428->0.0069 (-0.1358) | 3.5230->0.0874 (-3.4356) | 2.1408->0.0881 (-2.0527) | `GOOD`->`GOOD` | velocity limit hit lower grid bound |
| right_hip_pitch | 3->1 (-2) | 0.020->0.040 (0.020) | 3.75->1.00 (-2.75) | 0.0286->0.0050 (-0.0236) | 0.1661->0.0069 (-0.1592) | 3.1013->0.0892 (-3.0120) | 2.6398->0.1077 (-2.5321) | `GOOD`->`GOOD` | velocity limit hit lower grid bound |
| right_knee | 3->1 (-2) | 0.020->0.040 (0.020) | 3.00->1.00 (-2.00) | 0.0348->0.0060 (-0.0288) | 0.2062->0.0078 (-0.1984) | 4.8109->0.0899 (-4.7210) | 3.1864->0.0935 (-3.0929) | `GOOD`->`GOOD` | velocity limit hit lower grid bound |

## Knee Asymmetry

- `left_right_knee_new_velocity_limit`: `1.0000` vs `1.0000`, left_minus_right `0.0000`
- `left_right_knee_new_raw_tracking_p95`: `0.0078` vs `0.0078`, left_minus_right `-0.0000`
- `left_right_knee_new_model_p95`: `0.0050` vs `0.0060`, left_minus_right `-0.0010`

## Interpretation

- Use this comparison to decide whether the corrected-knee hardware changed the actuator bridge ranges.
- If the new fit is sine-only, do not treat it as walking-policy dynamic evidence.
- If left/right knee asymmetry remains large, inspect hardware before training around it.
