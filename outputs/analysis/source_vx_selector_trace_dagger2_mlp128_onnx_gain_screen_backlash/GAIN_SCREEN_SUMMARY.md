# DAgger-2 ONNX Action-Gain Screen
status: `HOLD_GAIN_SCREEN_NO_ENVELOPE_SAFE_MOTION`
Offline eval-only screen on `flat_terrain_backlash`, fitted bridge, seeds `0` and `3`, 5s. No policy file, runtime, robot, SSH, deploy, or training change was performed.

## Gain Summary
| gain | complete | moving ratio>=0.5 | mean_ratio | min_ratio | mean_vx | max_sent_vel_p95 | max_tracking_p95 | min_height |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.90 | 2/2 | 0/2 | 0.1780 | 0.0822 | 0.0142 | 3.8143 | 0.2329 | 0.1520 |
| 0.80 | 2/2 | 0/2 | -0.0437 | -0.1178 | -0.0035 | 0.8196 | 0.0941 | 0.1520 |
| 0.70 | 2/2 | 0/2 | -0.0587 | -0.1344 | -0.0047 | 0.2351 | 0.0568 | 0.1520 |
| 0.60 | 2/2 | 0/2 | -0.0646 | -0.1410 | -0.0052 | 0.2077 | 0.0465 | 0.1520 |

## Per Seed
| gain | seed | status | samples | term | mean_vx | ratio | sent_vel_p95_max | tracking_p95_max | height_min |
|---:|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0.90 | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0219 | 0.2737 | 3.8143 | 0.2329 | 0.1520 |
| 0.90 | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0066 | 0.0822 | 3.5044 | 0.2285 | 0.1551 |
| 0.80 | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0024 | 0.0303 | 0.8196 | 0.0941 | 0.1520 |
| 0.80 | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0094 | -0.1178 | 0.5655 | 0.0679 | 0.1545 |
| 0.70 | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0014 | 0.0171 | 0.1865 | 0.0568 | 0.1520 |
| 0.70 | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0107 | -0.1344 | 0.2351 | 0.0494 | 0.1540 |
| 0.60 | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0009 | 0.0117 | 0.1082 | 0.0465 | 0.1520 |
| 0.60 | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0113 | -0.1410 | 0.2077 | 0.0447 | 0.1534 |

## Interpretation
- The gain screen does not find a simple action-gain wrapper that both preserves forward tracking and brings max pitch-chain target velocity under the fitted envelope.
- Gain `0.90` preserves motion on the two screened seeds but still exceeds the envelope. Lower gains reduce target rate but make seed `3` miss the forward-tracking threshold.
- Do not turn this into a runtime gain hack; the useful result is that the next portable student needs training/distillation changes, not a scalar output multiplier.
