# Ground-Up Torso-COM MJX Initialization-Order Audit Contract

status: `PASS_TORSO_COM_MJX_INITIALIZATION_ORDER_CONTRACT`

All frozen pre-outcome checks passed:

- preregistration, base environment tool, prior invalid result, manifest, and
  three exact trace hashes match;
- `trunk_assembly` is massive body 2 and the immutable NEG/POS models change
  only `body_ipos[2,0]` by the exact model-dtype representation of -.05/+ .05;
- the name-resolved `accelerometer` is the three-axis sensor at address 6 on
  site `imu`;
- exact home `qpos`, zero `qvel`, and home `ctrl` shapes are finite;
- all frozen MJX data fields, including `qacc_warmstart` and `_impl`, exist;
- the seven frozen variants and exact primary-field copy list are present in
  the hash-locked study source;
- JAX exposed CPU only.

Execution counters are zero formal variant sensor reads, zero dynamic steps,
zero actor calls, zero training, and zero robot/RDK access. The contract JSON
SHA-256 is
`2205c30a1cde2ca8626f177db7e0aa11b7b9d9d96e347c7eb334b7306acf4a73`;
the locked tool SHA-256 is
`53821c1deb30ec2eb98dcfdb5ae380ebf17009ae5b22734bcc6499e6aa7e2e08`.

This pass authorizes only the preregistered seven-variant, single-state,
tick-zero CPU methods audit. It does not authorize a dynamic step, policy
call, 144-cell rerun, training, hardware, or deployment.
