# Ground-Up Torso-COM MJX Initialization-Order Audit Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_MJX_INITIALIZATION_ORDER_AUDIT`

## Evidence question

The exact-MJX 36-run map preserved all 21,600 baseline rows and the nominal
actor observation exactly, but failed its frozen tick-zero COM anchor by
.0133886337 m/s^2. This proves the remaining discrepancy is not baseline
trajectory perturbation, reporting-state indexing, or native-versus-MJX engine
choice. It occurs when an already-forwarded nominal `mjx.Data` is forwarded
under a replaced COM model instead of being initialized under that model.

This deterministic methods audit asks which MJX data-initialization component
is sufficient to reproduce the already-frozen NEG/POS tick-zero endpoint
sensors. It makes no policy, behavior, or training claim.

## Frozen sources and endpoint oracle

- invalid exact-MJX map result SHA-256:
  `23b4ad8444fc4eaa9dd83dcffb64b3b070431f3b424a83d71bf9a5b2a5ffcf3b`;
- exact replay manifest SHA-256:
  `ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07`;
- nominal tick-zero trace SHA-256:
  `e4a2452df4beaa703553bcb6b3f4e206d9e104258a48212ffe2d4f4541f1dd7c`;
- NEG tick-zero trace SHA-256:
  `e8ce3e5c559fcce85937c35118b6d55272ede022fd9c344dd033b5a5f058184d`;
- POS tick-zero trace SHA-256:
  `f18442447991fdd5c2be1caf0a08a966ec35e8b65173f86c518185b21a641c53`;
- exact composed playground/environment/model/reference hashes remain those in
  the preceding signed and exact-MJX contracts.

Use only row zero of A05_DIRECT_1003520, P30, x=.074, seed 167931544. The three
frozen accelerometer vectors are:

- NOMINAL: `[-11.879271507263184, .8971166610717773, 29.650177001953125]`;
- NEG: `[-13.04679012298584, .7727481126785278, 28.672449111938477]`;
- POS: `[-10.715840339660645, 1.0117170810699463, 30.856430053710938]`.

Their half-difference is the frozen direction
`d=[1.1654748916625977,.11948448419570923,1.0919904708862305]`.
Effective sample size is one deterministic reset state. No p-value,
replication, or population claim is allowed.

## Frozen model and reset

Construct the exact nominal CPU MJX model and two immutable models changing
only name-resolved `trunk_assembly` `body_ipos[2,0]` by -.05/+ .05 m. Use exact
home-support `qpos`, zero `qvel`, and home actuator control. The branch sensor is
the name-resolved three-axis `accelerometer` on `imu`.

Define `fresh_branch_data(model)=mjx.make_data(model)` followed by exact
home `qpos/qvel/ctrl` replacement and `mjx.forward(model,data)`. Define
`live_nominal_data` by the same operation under the nominal model.

## Frozen variants

For each variant, produce NEG and POS sensor vectors and compare them with the
frozen endpoint oracle. No variant may borrow endpoint data fields.

1. `FRESH_INIT_REFERENCE`: independently call
   `mujoco_playground._src.mjx_env.init` under each COM model with exact
   `qpos/qvel/ctrl`.
2. `LIVE_FORWARD_REPRODUCTION`: call `mjx.forward(COM_model,
   live_nominal_data)` unchanged. This must reproduce the preceding invalid
   method.
3. `LIVE_ZERO_WARMSTART`: zero only `qacc_warmstart` in live nominal data,
   then forward under the COM model.
4. `LIVE_FRESH_IMPL`: replace only the private `_impl` field with `_impl` from
   `mjx.make_data(COM_model)`, then forward.
5. `LIVE_ZERO_WARMSTART_FRESH_IMPL`: apply exactly both changes in variants 3
   and 4, then forward.
6. `FRESH_PRIMARY_COPY`: begin with `mjx.make_data(COM_model)`, copy exactly
   these non-derived/live input fields from live nominal data, then forward:
   `time,qpos,qvel,act,history,qacc_warmstart,plugin_state,ctrl,qfrc_applied,
   xfrc_applied,eq_active,mocap_pos,mocap_quat,userdata`.
7. `FRESH_PRIMARY_COPY_ZERO_WARMSTART`: variant 6 with only copied
   `qacc_warmstart` replaced by zeros.

The variants and field lists are frozen before any branch sensor is read. No
additional field, midpoint, tolerance, or reordered operation may be added
after outcomes.

## Frozen validity and classification

For each variant record:

- maximum absolute NEG endpoint error;
- maximum absolute POS endpoint error;
- maximum of those two endpoint errors;
- half-direction maximum error versus frozen `d`.

A variant is `MATCH_ENDPOINT_ORACLE` only if its combined endpoint maximum
error is <=1e-3 m/s^2. Otherwise it is `MISS_ENDPOINT_ORACLE`.

The audit is valid only if all hold:

- fresh nominal initialization matches frozen NOMINAL within 1e-3 m/s^2;
- `FRESH_INIT_REFERENCE` matches both endpoint vectors within 1e-3 m/s^2;
- `LIVE_FORWARD_REPRODUCTION` misses the oracle and reproduces the preceding
  exact-MJX invalid half-direction within 1e-6 m/s^2;
- all sensor values are finite;
- model mutation and CPU-only contracts pass.

Failure yields `INVALID_MJX_INITIALIZATION_ORDER_AUDIT`; no variant selection
is permitted.

## Frozen decision

Apply the first matching rule in order:

1. If LIVE_FORWARD unexpectedly matches: `INVALID_LIVE_REPRODUCTION_MISMATCH`.
2. If exactly one of `LIVE_ZERO_WARMSTART` or `LIVE_FRESH_IMPL` matches:
   `QACC_WARMSTART_SUFFICIENT` or `MJX_IMPL_SUFFICIENT`, respectively.
3. If neither individual variant matches but
   `LIVE_ZERO_WARMSTART_FRESH_IMPL` matches:
   `WARMSTART_AND_IMPL_JOINTLY_SUFFICIENT`.
4. If both individual variants match:
   `MULTIPLE_SINGLE_FIELD_RESETS_SUFFICIENT`.
5. If no live reset above matches but either fresh-primary variant matches:
   `FRESH_DERIVED_DATA_REQUIRED`.
6. Otherwise: `FULL_FRESH_INITIALIZATION_REQUIRED_OR_UNRESOLVED`.

These outcomes select only the named data-initialization mechanism for a
separately preregistered sensor-map correction. They do not authorize rerunning
the 144-cell map, actor forks, policy/reward changes, or training.

## Contract and authority boundary

Before formal endpoint reads, a committed CPU-only contract must verify exact
source/trace hashes, model/body/sensor identity, home-state arrays, MJX Data
field availability, exact frozen variant source structure, and zero formal
variant sensor reads.

This preregistration authorizes one contract and one seven-variant tick-zero
CPU methods audit. It authorizes no dynamic step, policy or actor call, outcome
retry, tolerance/variant/field change, training, Colab, GPU/iGPU, R2/R3,
runtime design, RDK-X5, robot access, deployment, torque, or motors.
