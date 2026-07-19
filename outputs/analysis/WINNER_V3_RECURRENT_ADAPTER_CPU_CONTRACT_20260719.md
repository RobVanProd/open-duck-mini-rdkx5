# Winner-v3 Recurrent-Adapter CPU Contract — 2026-07-19

Status: `HOLD_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT`

- JAX devices: `['TFRT_CPU_0']`
- source checkpoint directory SHA-256: `311ce59807ad872795dd95e4a30c626f11d3d80f1b3f78c5b2b997639da4d67e`
- step-zero maximum base/adapter logits error: `0.0`
- initial ONNX action/hidden error: `0.0` / `0.0`
- CPU smoke exports: `[0, 1024]`
- CPU smoke wall seconds: `105.856`
- base/adapter-state/adapter-head maximum updates: `0.012160848826169968` / `0.011715233325958252` / `0.0085181575268507`
- trained ONNX SHA-256: `916751a0fa15a890b3f2e7c6d6c2e973f87eda605fa6b873db5b647cf4325191`
- failed checks: `['expanded_hidden_normalizer_exact']`

This is a plumbing and finite-update contract only. Training reward and the
1,024-step policy behavior have no selection weight and make no gait claim. A
pass authorizes only the single preregistered CPU curriculum and its later
frozen CPU evaluation. It does not authorize Colab/hosted allocation,
GPU/iGPU, RDK-X5, robot, serial, torque, motion, runtime execution, Gate 5,
deployment, or robot clearance.
