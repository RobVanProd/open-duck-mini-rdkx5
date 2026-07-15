# Ground-Up Torso-COM Reset Estimator Feasibility Preregistration

status: `PREREGISTERED_READ_ONLY_CPU_RESET_COM_ESTIMATOR_FEASIBILITY`

## Evidence question

The corrected eager-MJX map establishes an exact, fixed-direction COM signal at
the deterministic reset (36/36 compatible, zero anchor error), while the same
physical signal becomes predominantly weak or nonlinear during gait. The
six contracted feedforward actors are materially accelerometer-responsive,
but their signed response is mixed and crossed localization is distributed or
unresolved. The corrected decode interpretation selects no feedforward arm.

This study asks the smallest remaining formulation question: can a frozen
estimator calibrated only at the already-contracted reset anchors
`{-0.05,0,+0.05} m` recover held-out interior torso X-COM offsets accurately
enough to justify a reset-latched estimator-input arm? It makes no policy,
training, robustness, or hardware claim.

## Frozen sources

- valid eager-MJX map result SHA-256:
  `05a12700ca6d9af6479fcb97a3c64109412a139efc24e369110c60ce8c1a9149`;
- decode interpretation correction SHA-256:
  `ef62ea7e479c1734dd8b416ce4bcb4636de9d4b5bf40c55cf729c8a536af1f37`;
- signed actor-response result SHA-256:
  `8c09ada8ce392c09fcee3cd9e7f449be5b1c50ca28b1640a4a3103755cc3b814`;
- crossed localization result SHA-256:
  `9c0823c7fce7bd409acbc53176c412dc45863f9c9ebaa27fa00a4f4597984ef0`;
- exact composed environment source SHA-256:
  `6e25285e9b12b8763aac0723e16c6d5ca63cac9e1956205fd44bdff714179b4d`;
- the exact CPU playground/model/scene/reference hashes, name-resolved body 2,
  `accelerometer` sensor on `imu`, home `qpos`, zero `qvel`, and home `ctrl`
  remain those in the passing eager-MJX and JIT-boundary contracts.

The frozen reset accelerometer anchors are:

- x=-.05: `[-13.04679012298584,.7727481126785278,28.672449111938477]`;
- x=0: `[-11.879271507263184,.8971166610717773,29.650177001953125]`;
- x=+.05: `[-10.715840339660645,1.0117170810699463,30.856430053710938]`.

Effective sample size is one deterministic reset curve. No p-value,
confidence, replication, or population claim is allowed.

## Frozen offsets and sensor method

Use exactly 11 offsets in ascending order:

`[-.05,-.04,-.03,-.02,-.01,0,.01,.02,.03,.04,.05] m`.

Only `-.05`, `0`, and `+.05` are calibration anchors. The eight interior
nonzero offsets are held-out evaluation points. For each offset, create an
immutable exact MJX model changing only name-resolved `trunk_assembly`
`body_ipos[2,0]`, call `mujoco_playground._src.mjx_env.init` eagerly with the
exact reset, and read the name-resolved three-axis accelerometer once. No JIT,
dynamic step, policy call, endpoint borrowing, or outcome retry is allowed.

## Frozen estimator

Let `a0`, `an`, and `ap` be the measured 0, negative-anchor, and
positive-anchor sensors. Define `un=an-a0` and `up=ap-a0`.

For each held-out sensor `a`, compute:

- `tn=clip(dot(a-a0,un)/dot(un,un),0,1)`, candidate `xn=-.05*tn`, and
  Euclidean residual to `a0+tn*un`;
- `tp=clip(dot(a-a0,up)/dot(up,up),0,1)`, candidate `xp=+.05*tp`, and
  Euclidean residual to `a0+tp*up`;
- choose the candidate with lower residual; an exact tie chooses the negative
  candidate.

The estimator, anchors, held-out points, clipping, norm, and tie rule are
frozen before any interior sensor is read. No fit is performed on held-out
points.

## Frozen validity and decision metrics

The study is method-valid only if:

- all three measured anchors match their frozen vectors within 1e-3 m/s^2
  maximum absolute error;
- each model changes only `body_ipos[2,0]` by its exact model-dtype offset;
- all sensors and estimator values are finite;
- JAX exposes CPU only.

Failure yields `INVALID_RESET_COM_ESTIMATOR_FEASIBILITY`; no estimator family
is selected.

For a valid study record:

- sign correctness at all eight held-out points;
- strict ordering of all eight estimates by actual offset;
- maximum absolute held-out offset error;
- Euclidean sensor separation for every adjacent 1 cm pair.

The 5 mm error ceiling is frozen at half the 1 cm held-out spacing and is only
a family-selection feasibility threshold. The adjacent sensor-separation floor
is the existing 1e-3 m/s^2 reset-anchor tolerance.

Apply the first matching decision:

1. If all signs are correct, estimates are strictly ordered, every adjacent
   sensor separation exceeds 1e-3 m/s^2, and maximum held-out error is <=.005 m:
   `SUPPORT_RESET_LATCHED_PIECEWISE_LINEAR_COM_ESTIMATOR_ARM`.
2. If signs, strict ordering, and separation pass but error exceeds .005 m:
   `SUPPORT_RESET_LATCHED_NONLINEAR_COM_ESTIMATOR_ARM`.
3. Otherwise:
   `RESET_ACCELEROMETER_CURVE_INSUFFICIENT_NO_ESTIMATOR_FAMILY_SELECTED`.

No closest result is promoted.

## Contract and authority boundary

Before formal sensor reads, a committed CPU-only contract must verify all
source/result hashes, body/sensor/reset identity, exact offsets, disjoint
anchor/held-out sets, frozen estimator source structure, one-sensor-read
cardinality, and zero formal offset sensor reads.

This preregistration authorizes one contract and one 11-point eager reset
curve. It authorizes no dynamic step, actor/policy call, training, Colab,
GPU/iGPU, retry, tolerance/offset/estimator change, robustness claim, R2/R3,
runtime design, RDK-X5, robot access, deployment, torque, or motors. A passing
decision authorizes only a separate preregistration for the named estimator
arm; it is not policy or robot clearance.
