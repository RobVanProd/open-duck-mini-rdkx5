# Ground-Up Torso-COM Exact MJX Accelerometer-Replay Contract

status: `PASS_TORSO_COM_EXACT_MJX_ACCELEROMETER_CONTRACT`

All zero-COM-outcome contract checks pass.

- Frozen sources and pre-instrumentation hashes match.
- Post-instrumentation hashes are locked:
  - `closed_loop_sim_eval.py`:
    `d2c452b19826e4ff9e399bf61fe09e654514c4fc194966871e35fba0850f20d7`;
  - `evaluate_ground_up_policy.py`:
    `347d3e4151d3f634710660b8c11bcce13724c66d33caafb5edbf86ebe2638030`;
  - formal study tool:
    `b28914ebe7ec4c2e200905862a577bda61d5a553ee0c6af3d6fd228313e6550c`.
- The new configuration is an empty tuple by default and all map work is
  guarded by the nonempty tick set.
- The only trace mutation is one conditional append-only map field.
- COM branch code calls `mjx.forward`; it contains no branch time step.
- Planned corpus is exactly 12 matrices, 36 moving runs, and 144 cells.
- One 600-tick default-off CPU regression passes gait emergence and reproduces
  the prior trace field-for-field and byte-for-byte. Generated and prior hashes
  are both
  `e4a2452df4beaa703553bcb6b3f4e206d9e104258a48212ffe2d4f4541f1dd7c`.
- The default-off trace contains zero map fields.
- Formal COM branch cells executed: zero.

The exact hash-locked formal replay is authorized. This contract does not
authorize actor counterfactuals, training, Colab, GPU/iGPU, RDK-X5, runtime, or
robot work.

Machine-readable record:
`ground_up_torso_com_exact_mjx_accelerometer_contract.json`.
