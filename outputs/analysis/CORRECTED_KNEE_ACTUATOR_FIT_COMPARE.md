# Actuator Response Fit Compare

status: `PASS_ACTUATOR_FIT_COMPARE_READY`

Offline comparison only. No robot tests, SSH, deployment, training, or runtime behavior changes were performed.

## Inputs

- old fit: `outputs/analysis/actuator_response_fit.json`
- old telemetry: `outputs/first_evidence/20260621T215022Z/suspended_policy_replay_x008_thresholds.jsonl`
- new fit: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- new telemetry: `outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl`

## Per-Joint Delta

| joint | delay old->new | tau old->new | vel old->new | model p95 old->new | raw p95 old->new | target vel p95 old->new | actual vel p95 old->new | quality old->new | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_ankle | 3->3 (0) | 0.020->0.020 (0.000) | 3.00->2.75 (-0.25) | 0.0193->0.0166 (-0.0027) | 0.1325->0.1474 (0.0149) | 3.7399->3.7867 (0.0468) | 2.1407->2.1208 (-0.0199) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| left_hip_pitch | 3->3 (0) | 0.020->0.020 (0.000) | 2.50->2.50 (0.00) | 0.0252->0.0267 (0.0015) | 0.1736->0.1850 (0.0113) | 5.2170->5.2169 (-0.0001) | 2.4047->2.4889 (0.0843) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| left_knee | 3->3 (0) | 0.020->0.020 (0.000) | 3.50->3.25 (-0.25) | 0.0333->0.0248 (-0.0085) | 0.1793->0.1968 (0.0175) | 3.7814->3.6614 (-0.1199) | 2.9371->2.7882 (-0.1489) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| right_ankle | 3->3 (0) | 0.020->0.020 (0.000) | 2.25->2.00 (-0.25) | 0.0273->0.0211 (-0.0062) | 0.1428->0.1448 (0.0020) | 3.5230->3.5194 (-0.0036) | 2.1408->1.9909 (-0.1499) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| right_hip_pitch | 3->3 (0) | 0.020->0.020 (0.000) | 3.75->2.25 (-1.50) | 0.0286->0.0259 (-0.0027) | 0.1661->0.1518 (-0.0144) | 3.1013->3.0992 (-0.0021) | 2.6398->2.2899 (-0.3499) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| right_knee | 3->3 (0) | 0.020->0.020 (0.000) | 3.00->2.75 (-0.25) | 0.0348->0.0335 (-0.0012) | 0.2062->0.2058 (-0.0004) | 4.8109->4.4553 (-0.3556) | 3.1864->2.9372 (-0.2493) | `GOOD`->`GOOD` | tau_s hit lower grid bound |

## Knee Asymmetry

- `left_right_knee_new_velocity_limit`: `3.2500` vs `2.7500`, left_minus_right `0.5000`
- `left_right_knee_new_raw_tracking_p95`: `0.1968` vs `0.2058`, left_minus_right `-0.0090`
- `left_right_knee_new_model_p95`: `0.0248` vs `0.0335`, left_minus_right `-0.0088`

## Interpretation

- Use this comparison to decide whether the corrected-knee hardware changed the actuator bridge ranges.
- If the new fit is sine-only, do not treat it as walking-policy dynamic evidence.
- If left/right knee asymmetry remains large, inspect hardware before training around it.
