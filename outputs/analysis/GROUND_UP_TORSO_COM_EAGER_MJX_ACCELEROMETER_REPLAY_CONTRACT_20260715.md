# Ground-Up Torso-COM Eager-MJX Accelerometer Replay Contract

status: `PASS_TORSO_COM_EAGER_MJX_ACCELEROMETER_CONTRACT`

All zero-formal-cell checks pass:

- preregistration, prior invalid exact map, valid JIT audit, replay manifest,
  and pre-correction evaluator hashes match;
- the only diagnostic runner assignment is the validated eager closure and all
  map work remains guarded by the empty default tick tuple;
- the branch calls `mjx.forward` and contains no time step;
- append-only trace and CLI default-off contracts remain exact;
- the planned corpus is 12 matrices, 36 runs, and 144 cells;
- one complete 600-tick CPU default-off regression passes gait emergence and
  reproduces the prior trace field-for-field and byte-for-byte at SHA-256
  `e4a2452df4beaa703553bcb6b3f4e206d9e104258a48212ffe2d4f4541f1dd7c`;
- that trace contains zero map fields and zero formal COM cells were executed.

The machine-readable contract SHA-256 is
`086cfc2c834459e36b65aebc675c7a0d1a18709abcc6a418b981317574750922`.
Locked source hashes are:

- study tool: `8fc5947ab87d7265c4a0f70ca422f713b1e602d9b550a3a22fbd8b7c850645f1`;
- closed-loop evaluator:
  `4df1d42aed855277abc2e5054cfe09a8de4c2c01706aa63f3698414a57bc56ab`;
- evaluator CLI:
  `347d3e4151d3f634710660b8c11bcce13724c66d33caafb5edbf86ebe2638030`.

This pass authorizes only the frozen corrected 36-run/144-cell CPU reporting
replay. It does not authorize actor counterfactuals, training, hardware, or
deployment.
