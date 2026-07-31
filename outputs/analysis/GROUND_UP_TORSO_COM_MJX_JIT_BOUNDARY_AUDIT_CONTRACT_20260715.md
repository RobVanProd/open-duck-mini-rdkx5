# Ground-Up Torso-COM MJX JIT-Boundary Audit Contract

status: `PASS_TORSO_COM_MJX_JIT_BOUNDARY_CONTRACT`

All frozen pre-outcome checks passed:

- initialization result/contract, evaluator sources, and preregistration hashes
  match;
- the preceding initialization audit is invalid exactly as recorded and its
  zero-outcome contract passed;
- `trunk_assembly` is body 2 and the NEG/POS immutable model changes are exact
  and X-only;
- the name-resolved three-axis `accelerometer` remains at address 6 on `imu`;
- exact home `qpos`, zero `qvel`, and home `ctrl` are finite;
- the four variant structures and NEG-before-POS sequential calls are frozen
  in the hash-locked source;
- JAX exposed CPU only.

Execution counters are zero formal endpoint reads, zero dynamic steps, zero
actor calls, zero training, and zero robot/RDK access. The contract JSON
SHA-256 is
`140b840a1438c8c8345828c8918ff282e3f71e2d239b50c9a31c4ae5f2723a44`;
the locked tool SHA-256 is
`562df47d52f750b8d13f01c953cd3a23c7af0a12cb24f71382e627681a77471c`.

This pass authorizes only the preregistered four-variant, single-state,
tick-zero CPU JIT-boundary audit. It does not authorize dynamic simulation,
policy calls, the 144-cell map, training, hardware, or deployment.
