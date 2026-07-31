# Winner-v3 Recurrent-Adapter CPU Contract — 2026-07-19

Status: `PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT`

The committed initial result at `215a84a1b526510bf7a82128ebff5637c2e216d8` held on one stale
normalizer-count assertion. It compared the neutral recurrent variance with
`8,048,640`, copied from the other persistent checkpoint, while the protected
T2_EQUAL 512K source and the formal expanded checkpoint both carry count
`7,536,640`. The same formal artifacts prove the 64 recurrent entries
are exactly mean zero, standard deviation one, and summed variance equal to
that source count. No training, export, inference, or behavior cell was rerun.

- JAX devices: `['TFRT_CPU_0']`
- step-zero maximum base/adapter logits error: `0.0`
- initial ONNX action/hidden error: `0.0` / `0.0`
- CPU smoke exports: `[0, 1024]`
- CPU smoke wall seconds: `105.856`
- base/adapter-state/adapter-head maximum updates: `0.012160848826169968` / `0.011715233325958252` / `0.0085181575268507`
- trained ONNX SHA-256: `916751a0fa15a890b3f2e7c6d6c2e973f87eda605fa6b873db5b647cf4325191`
- failed checks after read-only correction: `[]`

This is a plumbing and finite-update contract only. Training reward and the
1,024-step behavior have no selection weight and make no gait claim. The pass
authorizes only the single preregistered CPU curriculum and its later frozen
CPU evaluation. It does not authorize hosted/Colab allocation, GPU/iGPU,
RDK-X5, robot, serial, torque, motion, runtime execution, Gate 5, deployment,
or robot clearance.
