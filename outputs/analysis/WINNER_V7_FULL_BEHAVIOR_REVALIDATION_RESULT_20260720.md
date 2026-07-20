# Winner-v7 Full Behavior Revalidation Result

Status: `HOLD_WINNER_V7_FULL_BEHAVIOR_REVALIDATION`

Decision: `CLOSE_WINNER_V7_PROTECTED_BASE`

Imported JSON SHA-256: `f181b7337e67c0b0d11d9a96b84ca0506ae689b49c5cb6de66a9f9811eb4f41e`

- raw result SHA-256: `39f5bae6f1cd216d1ca18f35b24bd4081e38fa7d1a873592f94c2f179379e94c`
- failed checks: `['all_current_protection_gates_pass']`
- worst tracking p95: `0.18337889909744262` rad
- worst peak current: `4.117104234210315` A
- longest consecutive duration above 2 A: `10` ticks

All 128 cells, behavior expectations, dynamics readbacks, transformed-policy hashes, CPU attestations, and trace continuity checks were present. Behavior was preserved, but the frozen 2.5 A peak-current protection gate failed. The exact winner-v7 protected base is closed and is not retried or reclassified.

No trace or ONNX binary is committed by this import. No training, runtime, robot access, torque, motion, Gate 5, deployment, or clearance is authorized.
