# Ground-Up Torso-COM Signed Causal-Response Contract

status: `PASS_TORSO_COM_SIGNED_RESPONSE_CONTRACT`

The frozen CPU-only pre-outcome contract passes every check. It executed zero
formal study cells.

- Selected source corpus: 36 exact nominal moving traces.
- Planned formal matrix: 144 cells.
- ONNX execution: all six contracted graphs on `CPUExecutionProvider` only.
- JAX device: `TFRT_CPU_0` only.
- Exact recurrent baseline maximum error: 0.
- Saved fork-action maximum error: 3.725290298461914e-09.
- Actuator bridge, sent-target, and applied-target maximum reconstruction error:
  5.1498413089490214e-08 rad.
- Matched identical-branch maximum error: 0.
- Corrected COM intervention: only `body_ipos[2,0]` on `trunk_assembly` changes.
- The fixed smoke branch confirms nonzero physical and actor interventions but
  is not a formal cell and makes no selection claim.

The contracted evaluator SHA-256 is
`6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d`.
Only that exact tool is authorized to execute the frozen 144-cell study. This
does not authorize training, Colab, GPU/iGPU, RDK-X5, runtime, or robot work.

Machine-readable record:
`ground_up_torso_com_signed_response_contract.json`.
