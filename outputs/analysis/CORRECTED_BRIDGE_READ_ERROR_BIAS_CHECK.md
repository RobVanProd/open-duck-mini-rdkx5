# Actuator Response Fit Compare

status: `PASS_ACTUATOR_FIT_COMPARE_READY`

Offline comparison only. No robot tests, SSH, deployment, training, or runtime behavior changes were performed.

## Inputs

- old fit: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- old telemetry: `outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl`
- new fit: `outputs/analysis/actuator_response_fit_corrected_knee_exclude_read_events.json`
- new telemetry: `/tmp/corrected_dynamic_replay_exclude_read_events_pm2.jsonl`

## Per-Joint Delta

| joint | delay old->new | tau old->new | vel old->new | model p95 old->new | raw p95 old->new | target vel p95 old->new | actual vel p95 old->new | quality old->new | warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| left_ankle | 3->3 (0) | 0.020->0.020 (0.000) | 2.75->2.75 (0.00) | 0.0166->0.0301 (0.0135) | 0.1474->0.1484 (0.0010) | 3.7867->4.2537 (0.4670) | 2.1208->2.3547 (0.2339) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| left_hip_pitch | 3->3 (0) | 0.020->0.020 (0.000) | 2.50->2.75 (0.25) | 0.0267->0.0492 (0.0225) | 0.1850->0.1898 (0.0048) | 5.2169->5.2171 (0.0002) | 2.4889->2.7383 (0.2493) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| left_knee | 3->3 (0) | 0.020->0.020 (0.000) | 3.25->6.00 (2.75) | 0.0248->0.0895 (0.0648) | 0.1968->0.1974 (0.0006) | 3.6614->3.9695 (0.3081) | 2.7882->2.9870 (0.1989) | `GOOD`->`USEFUL` | tau_s hit lower grid bound, velocity limit hit upper grid bound |
| right_ankle | 3->3 (0) | 0.020->0.020 (0.000) | 2.00->2.25 (0.25) | 0.0211->0.0507 (0.0296) | 0.1448->0.1448 (0.0000) | 3.5194->3.7581 (0.2387) | 1.9909->1.9916 (0.0007) | `GOOD`->`USEFUL` | tau_s hit lower grid bound |
| right_hip_pitch | 3->3 (0) | 0.020->0.020 (0.000) | 2.25->2.25 (0.00) | 0.0259->0.0419 (0.0160) | 0.1518->0.1515 (-0.0003) | 3.0992->3.3179 (0.2187) | 2.2899->2.3053 (0.0153) | `GOOD`->`GOOD` | tau_s hit lower grid bound |
| right_knee | 3->3 (0) | 0.020->0.020 (0.000) | 2.75->2.75 (0.00) | 0.0335->0.0845 (0.0509) | 0.2058->0.2043 (-0.0015) | 4.4553->4.7246 (0.2693) | 2.9372->3.0367 (0.0995) | `GOOD`->`USEFUL` | tau_s hit lower grid bound |

## Knee Asymmetry

- `left_right_knee_new_velocity_limit`: `6.0000` vs `2.7500`, left_minus_right `3.2500`
- `left_right_knee_new_raw_tracking_p95`: `0.1974` vs `0.2043`, left_minus_right `-0.0069`
- `left_right_knee_new_model_p95`: `0.0895` vs `0.0845`, left_minus_right `0.0051`

## Interpretation

- Use this comparison to decide whether the corrected-knee hardware changed the actuator bridge ranges.
- If the new fit is sine-only, do not treat it as walking-policy dynamic evidence.
- If left/right knee asymmetry remains large, inspect hardware before training around it.
