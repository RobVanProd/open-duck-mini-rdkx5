# Ground-Up Torso-COM Crossed Phase-Localization Contract

status: `PASS_TORSO_COM_CROSSED_PHASE_CONTRACT`

The frozen CPU-only contract passes all checks and executes zero formal crossed
cells.

- Exact source traces: 36.
- Complete planned matrix: 576 cells (144 diagonal, 432 off-diagonal).
- Planned first-branch raw actions: 1,152.
- Raw action range: [-.9697054625, .9726300240]; no planned clipping.
- Minimum negative/positive donor-offset norms: .0115319930/.0132588735.
- All six contracted ONNX graphs use `CPUExecutionProvider` only.
- JAX device: `TFRT_CPU_0` only.
- Maximum recurrent baseline error: 0.
- Maximum bridge, sent-target, and applied-target reconstruction error:
  5.1498413089490214e-08 rad.
- Source signed-result, signed-contract, preregistration, evaluator, trace,
  graph, fit, scene, environment, and reference hashes pass.

The contracted crossed evaluator SHA-256 is
`be2636192ce2de8abf0a0d166353e69083ed29559829dc6789a4a863dbc81c87`.
Only that exact tool may execute the frozen matrix. During formal execution the
144 diagonal cells must reproduce the prior signed pitch trajectories and
alignment within 1e-12 or the complete study is invalid.

This contract authorizes only the exact CPU crossed study. It authorizes no
training, Colab, GPU/iGPU, RDK-X5, runtime, or robot work.

Machine-readable record:
`ground_up_torso_com_crossed_phase_contract.json`.
