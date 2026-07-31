# Ground-Up Torso-COM Reset Estimator Feasibility Contract

status: `PASS_RESET_COM_ESTIMATOR_FEASIBILITY_CONTRACT`

All frozen pre-outcome checks pass:

- upstream map/decode/signed/crossed decisions and source hashes match;
- `trunk_assembly` is massive body 2 and the name-resolved three-axis
  `accelerometer` remains at address 6 on `imu`;
- exact home `qpos`, zero `qvel`, and home `ctrl` are finite;
- 11 ordered offsets split exactly into three anchors and eight disjoint
  held-out points;
- every immutable model uses the exact model-dtype body-2 X addition and
  changes no other element;
- AST inspection finds exactly one eager `mjx_env.init` call and one sensor
  slice in the offset loop, with no JIT or `mjx.step` call;
- the frozen estimator equations and thresholds are present in the hash-locked
  source;
- JAX exposes CPU only.

Execution counters are zero formal offset sensor reads, zero dynamic steps,
zero actor calls, zero training, and zero robot/RDK access. The machine-readable
contract SHA-256 is
`03947777cdd350cc8ec88e299ce651adc46c7f6682f15d64900238386004ecc7`;
the locked tool SHA-256 is
`bd38e5a2644655c76a7d0021b2bc10c46fe7475dceb16226f18b6affd98807d9`.

This pass authorizes only the preregistered 11-point eager reset curve. It does
not authorize dynamic simulation, policy calls, training, hardware, or
deployment.
