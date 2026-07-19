# Winner-v2 Native-Quantized Checkpoint Selection Result

status: `PASS_NATIVE_QUANTIZED_CHECKPOINT_SELECTED`
decision: `SELECT_WINNER_V2_512000_NATIVE_QUANTIZED`
selected ONNX SHA-256: `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`

| checkpoint | all 8 cells pass | worst tracking p95 | minimum moving vx | source SHA-256 |
|---:|---|---:|---:|---|
| 512000 | `True` | 0.180925965309 | 0.082922109540 | `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de` |
| 1024000 | `True` | 0.181829959154 | 0.093250979375 | `0dfc24bde5d839e4d346dd8c08d9a7d0222a3847764ec6738bfc7f8d947f4ece` |

The selection rule was frozen before these representation outcomes. Training and simulator reward had zero selection weight. The selected identity, if any, is the original policy graph; the quantized wrapper is evaluation-only because the native runtime supplies register-quantized inputs.

This result covers finite native input representation only. It does not cover sensor bias/noise/age or real torso COM, and it does not authorize Gate 5, deployment, RDK-X5/robot access, torque, motors, or robot clearance.
