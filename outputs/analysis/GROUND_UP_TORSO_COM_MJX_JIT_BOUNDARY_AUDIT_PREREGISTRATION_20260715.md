# Ground-Up Torso-COM MJX JIT-Boundary Audit Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_MJX_JIT_BOUNDARY_AUDIT`

## Evidence question

The initialization-order audit was invalid because its standalone
`LIVE_FORWARD_REPRODUCTION` matched the frozen endpoint oracle exactly rather
than reproducing the exact evaluator map's .0133886337 m/s^2 tick-zero
half-direction error. Source inspection shows the home-support evaluator uses
`mjx_env.init` and that its later observation refresh does not replace
`state.data`. The remaining explicit methods difference is the exact map's
JIT-compiled branch-forward closure.

This single-state audit asks whether that JIT boundary reproduces the prior
invalid result and, if it does, whether external model construction or paired
endpoint evaluation removes it. It makes no behavior or policy claim.

## Frozen sources and oracle

- initialization-order result SHA-256:
  `41e3c6184b4857448bc4600c7f6bf96f944e0dbc4485a00f36bb96c948538864`;
- initialization-order contract SHA-256:
  `2205c30a1cde2ca8626f177db7e0aa11b7b9d9d96e347c7eb334b7306acf4a73`;
- exact evaluator core SHA-256:
  `d2c452b19826e4ff9e399bf61fe09e654514c4fc194966871e35fba0850f20d7`;
- evaluator CLI SHA-256:
  `347d3e4151d3f634710660b8c11bcce13724c66d33caafb5edbf86ebe2638030`;
- the base tool, manifest, three trace hashes, model, reset, sensor, and exact
  NOMINAL/NEG/POS vectors remain frozen exactly as in the initialization-order
  preregistration.

The oracle half-direction is
`[1.1654748916625977,.11948448419570923,1.0919904708862305]`. The preceding
invalid exact-map half-direction is
`[1.1723289489746094,.11886221170425415,1.0786018371582031]`.
Effective sample size is one deterministic reset state. No p-value,
replication, or population claim is authorized.

## Frozen model, data, and endpoint order

Use the exact nominal CPU MJX model; immutable NEG/POS models change only
name-resolved `trunk_assembly` `body_ipos[2,0]` by -.05/+ .05 m. Construct the
single `live_nominal_data` with `mjx_env.init(nominal_model, home_qpos,
zero_qvel, home_ctrl)`. The name-resolved sensor is the three-axis
`accelerometer` on `imu`.

Every sequential variant evaluates NEG first and POS second. JIT runners are
constructed once and reused exactly as specified. No warm-up endpoint call,
retry, reversed order, or additional compilation is allowed.

## Frozen variants

1. `EAGER_REPLACE_INSIDE`: the exact evaluator closure without `jax.jit`:
   accept `(data, body_ipos)`, replace `nominal_model.body_ipos` inside the
   function, call `mjx.forward`, and read the sensor; call NEG then POS.
2. `JIT_REPLACE_INSIDE_SEQUENTIAL`: wrap exactly variant 1 in `jax.jit`, then
   call NEG and POS sequentially. This is the exact prior evaluator boundary.
3. `JIT_MODEL_ARGUMENT_SEQUENTIAL`: construct immutable NEG/POS models outside
   the compiled function; JIT one function accepting `(model,data)`, forward
   and read the sensor; call NEG then POS.
4. `JIT_PAIR_REPLACE_INSIDE`: JIT one function accepting
   `(data,negative_body_ipos,positive_body_ipos)`, construct both replaced
   models inside, forward both from the same data, and return both sensors in
   one call.

No other JIT option, precision flag, device setting, field reset, or variant
may be added after outcomes.

## Frozen classification and validity

For each variant record both endpoint vectors, maximum NEG/POS/combined oracle
error, half-direction, and half-direction maximum error. Endpoint match is
`MATCH_ENDPOINT_ORACLE` only at combined error <=1e-3 m/s^2.

The audit is valid only if all hold:

- the exact eager closure matches both oracle endpoints within 1e-3 m/s^2;
- `JIT_REPLACE_INSIDE_SEQUENTIAL` misses the endpoint oracle and reproduces
  the preceding invalid half-direction within 1e-6 m/s^2;
- all values are finite and the frozen model/CPU contracts pass.

Failure yields `INVALID_MJX_JIT_BOUNDARY_AUDIT`; no mechanism is selected.

## Frozen decision

If valid, apply the first matching rule:

1. If both control variants match:
   `MULTIPLE_JIT_BOUNDARY_REMEDIES_MATCH_ORACLE`.
2. If only `JIT_MODEL_ARGUMENT_SEQUENTIAL` matches:
   `CONSTRUCT_MODEL_OUTSIDE_JIT_SUFFICIENT`.
3. If only `JIT_PAIR_REPLACE_INSIDE` matches:
   `PAIRED_ENDPOINT_JIT_SUFFICIENT`.
4. If neither matches:
   `GENERAL_JIT_FORWARD_DISCREPANCY_OR_UNRESOLVED`.

The decision selects only a candidate evaluation-method correction for a
separately preregistered exact-map validation. It does not authorize the
144-cell map, actor forks, policy work, or training.

## Contract and authority boundary

Before formal endpoint reads, a committed CPU-only contract must verify exact
source/result/trace hashes, model/body/sensor/reset identity, the four frozen
variant source structures, NEG-then-POS order, and zero formal endpoint reads.

This preregistration authorizes one contract and one four-variant tick-zero CPU
methods audit. It authorizes no dynamic step, policy/actor call, outcome retry,
training, Colab, GPU/iGPU, R2/R3, runtime design, RDK-X5, robot access,
deployment, torque, or motors.
