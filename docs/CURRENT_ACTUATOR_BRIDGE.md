# Current Actuator Bridge

Status: `CORRECTED_DYNAMIC_BRIDGE_CANONICAL`

Use this file as the short pointer for future sim/eval/training work.

## Current Fit

```text
path: outputs/analysis/actuator_response_fit_corrected_knee.json
sha256: 3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0
source: corrected suspended x=0.08 dynamic replay
selection_metric: trimmed_rmse_95
status: canonical for future candidate gates
```

## Deprecated Fit

```text
path: outputs/analysis/actuator_response_fit.json
sha256: 9e0a8e489469b76e3a41bc44fb7e1398b57e13c7da723484a913127b24bc6959
source: pre-left-knee-correction replay
status: historical only
```

## Low-Speed Sanity Fit

```text
path: outputs/analysis/actuator_response_fit_corrected_knee_sine_only.json
status: low-speed sanity only; not a walking approval bridge
```

## Corrected Pitch-Chain Limits

| joint | velocity limit rad/s |
|---|---:|
| left_hip_pitch | 2.50 |
| left_knee | 3.25 |
| left_ankle | 2.75 |
| right_hip_pitch | 2.25 |
| right_knee | 2.75 |
| right_ankle | 2.00 |

Candidate gates must use these per-joint limits rather than the old global
`3.75 rad/s` threshold.
