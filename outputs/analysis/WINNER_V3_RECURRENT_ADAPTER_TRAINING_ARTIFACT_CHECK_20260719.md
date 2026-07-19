# Winner-v3 Recurrent-Adapter Training Artifact Check — 2026-07-19

Status: `PASS_WINNER_V3_RECURRENT_ADAPTER_TRAINING_ARTIFACT_CHECK`

- archive SHA-256: `bee604f002df5082bce579734be5a7983f2b31a6026b1caaa34d64b26ce48d91`
- archive bytes / members: `23521941 / 171`
- JAX devices: `['TFRT_CPU_0']`
- stage restore continuity max errors: `[0.0, 0.0]`
- persistent ONNX: `[{'step': 1003520, 'sha256': '3d5e6dd447601246f8f5789ce370a1d63648334536359f367f0cb856ab77b04d'}, {'step': 2007040, 'sha256': 'fb725c5e8f45866c9b96e56b2429774f2e1ce73261ffb33ff534d977195544f0'}]`
- formal behavior cells executed: `0`
- failed checks: `[]`

This is an independent CPU artifact/continuity/ABI check. A pass authorizes only
the already-frozen 1,024-cell CPU behavior evaluation. It is not behavior
evidence, a supported-configuration envelope, runtime acceptance, Gate 5,
deployment, or robot clearance. No hosted allocation, GPU/iGPU, RDK-X5, robot,
serial, torque or motion is authorized.
