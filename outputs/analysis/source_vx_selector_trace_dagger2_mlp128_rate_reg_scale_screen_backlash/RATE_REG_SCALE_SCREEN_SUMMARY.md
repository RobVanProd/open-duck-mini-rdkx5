# DAgger-2 ONNX Target-Rate Regularization Scale Screen
status: `HOLD_RATE_REG_SCALE_SWEEP_NO_BALANCED_PASS`
Offline task-matched standard ONNX screen on `flat_terrain_backlash`, fitted bridge, seeds `0` and `3`, 10s. No robot test, SSH, deploy, runtime behavior change, or hardware motion was performed.

## Scale Summary
| target_rate_scale | complete | moving ratio>=0.5 | mean_ratio | min_ratio | mean_vx | max_sent_vel_p95 | max_tracking_p95 | min_height |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.03 | 2/2 | 0/2 | 0.4583 | 0.4353 | 0.0367 | 3.7688 | 0.2489 | 0.1520 |
| 0.05 | 2/2 | 1/2 | 0.4571 | 0.4090 | 0.0366 | 3.6952 | 0.2477 | 0.1520 |
| 0.10 | 2/2 | 0/2 | 0.4104 | 0.3616 | 0.0328 | 3.6419 | 0.2461 | 0.1520 |

## Per Seed
| scale | seed | status | samples | term | mean_vx | ratio | sent_vel_p95_max | tracking_p95_max | height_min |
|---:|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0.03 | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0385 | 0.4812 | 3.7688 | 0.2470 | 0.1520 |
| 0.03 | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0348 | 0.4353 | 3.7355 | 0.2489 | 0.1551 |
| 0.05 | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0404 | 0.5052 | 3.6760 | 0.2453 | 0.1520 |
| 0.05 | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0327 | 0.4090 | 3.6952 | 0.2477 | 0.1553 |
| 0.10 | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0367 | 0.4592 | 3.6419 | 0.2461 | 0.1520 |
| 0.10 | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0289 | 0.3616 | 3.6396 | 0.2458 | 0.1552 |

## Interpretation
- No screened target-rate scale preserves track ratio >= 0.5 on both seeds while keeping max pitch-chain sent-target p95 <= 3.75 rad/s.
- Scale `0.03` keeps seed 0 moving but seed 3 falls below the forward gate and max target velocity remains above the envelope.
- Scales `0.05` and `0.10` bring target velocity under the envelope but reduce forward tracking below the gate.
- This argues against merely increasing the existing pairwise target-rate penalty; the next portable student needs a different objective or policy class that preserves the blend/selector closed-loop behavior.
