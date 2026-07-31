# Actuator Response Fit Compare

status: `PASS_ACTUATOR_FIT_COMPARE_READY`

Offline comparison only. No robot tests, SSH, deployment, training, or runtime behavior changes were performed.

## Inputs

- old fit: `outputs/analysis/actuator_response_fit.json`
- old telemetry: `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl`
- new fit: `outputs/analysis/actuator_response_fit.json`
- new telemetry: `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl`

## Per-Joint Delta

| joint | delay old->new | tau old->new | vel old->new | model p95 old->new | raw p95 old->new | target vel p95 old->new | actual vel p95 old->new | quality old->new | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_ankle | 3->3 (0) | 0.020->0.020 (0.000) | 3.00->3.00 (0.00) | 0.0193->0.0193 (0.0000) | 0.1325->0.1325 (0.0000) | 3.7399->3.7399 (0.0000) | 2.1407->2.1407 (0.0000) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| left_hip_pitch | 3->3 (0) | 0.020->0.020 (0.000) | 2.50->2.50 (0.00) | 0.0252->0.0252 (0.0000) | 0.1736->0.1736 (0.0000) | 5.2170->5.2170 (0.0000) | 2.4047->2.4047 (0.0000) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| left_knee | 3->3 (0) | 0.020->0.020 (0.000) | 3.50->3.50 (0.00) | 0.0333->0.0333 (0.0000) | 0.1793->0.1793 (0.0000) | 3.7814->3.7814 (0.0000) | 2.9371->2.9371 (0.0000) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| right_ankle | 3->3 (0) | 0.020->0.020 (0.000) | 2.25->2.25 (0.00) | 0.0273->0.0273 (0.0000) | 0.1428->0.1428 (0.0000) | 3.5230->3.5230 (0.0000) | 2.1408->2.1408 (0.0000) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| right_hip_pitch | 3->3 (0) | 0.020->0.020 (0.000) | 3.75->3.75 (0.00) | 0.0286->0.0286 (0.0000) | 0.1661->0.1661 (0.0000) | 3.1013->3.1013 (0.0000) | 2.6398->2.6398 (0.0000) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| right_knee | 3->3 (0) | 0.020->0.020 (0.000) | 3.00->3.00 (0.00) | 0.0348->0.0348 (0.0000) | 0.2062->0.2062 (0.0000) | 4.8109->4.8109 (0.0000) | 3.1864->3.1864 (0.0000) | `GOOD`->`GOOD` | tau_s hit lower grid bound |

## Knee Asymmetry

- `left_right_knee_new_velocity_limit`: `3.5000` vs `3.0000`, left_minus_right `0.5000`
- `left_right_knee_new_raw_tracking_p95`: `0.1793` vs `0.2062`, left_minus_right `-0.0269`
- `left_right_knee_new_model_p95`: `0.0333` vs `0.0348`, left_minus_right `-0.0015`

## Interpretation

- Use this comparison to decide whether the corrected-knee hardware changed the actuator bridge ranges.
- If the new fit is sine-only, do not treat it as walking-policy dynamic evidence.
- If left/right knee asymmetry remains large, inspect hardware before training around it.
